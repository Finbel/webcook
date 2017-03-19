from .forms import RecipeIngredientForm, RecipeForm, CalorieForm, ServingsForm, CommentForm, SpecificCalorieForm
from .models import Recipe, Ingredient, RecipeIngredient, Unit, RecipeOwner, IngredientUnitToCal, UserHistory, RecipeComment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import formset_factory
from django.forms import BaseFormSet
import datetime
 
# Create your views here.
def home(request):
    return render(request, 'cook_app/home.html', {})

#get_recipe_structure is a help method that takes in the ammount of serving and the key of a recipe and then returns all the information needed to create a template for a recipe
@login_required
def get_recipe_structure(recipe_pk, servings):
    #gets the recipe based on the id
    recipe = Recipe.objects.get(id=recipe_pk)
    #sets name to the title so that we can easily send it back
    name = recipe.title
    #gets the owner of the recipe
    recipe_owner = RecipeOwner.objects.get(recipe__id=recipe_pk)
    #gets the description of the recipe
    description = recipe_owner.description
    #gets the name of the owner
    owner = recipe_owner.owner.username
    ingredient_structure = []
    #gets all of the ingredients for the recipe
    recipe_ingredients = RecipeIngredient.objects.filter(recipe__id=recipe_pk)
 
    ingredient_tuples = []
    for recipe_ingredient in recipe_ingredients:
        #gets the IngredientUnitToCal object based on the ingredient and unit keys
        converter = IngredientUnitToCal.objects.get(ingredient=recipe_ingredient.ingredient, unit=recipe_ingredient.unit)
        #puts the ingredient into the touple we will use later, where recipe_Ingredient and the IngredientUnitToCal are the touple 
        ingredient_tuples.append((recipe_ingredient,converter))
    #intializes values
    cal = 0
    cal_per_serving = 0
    #loops over the tuples
    for ingredient_tuple in ingredient_tuples:
        #takes out each part of the touple
        recipe_ingredient = ingredient_tuple[0]
        ingred_unit_cal = ingredient_tuple[1]
        #assert ingredient name and unit to variables
        ingredient_name = recipe_ingredient.ingredient.name
        ingredient_unit = recipe_ingredient.unit.unit
        #checks if we have intialized the amount of calories the unit has
        if(ingred_unit_cal.ingredient_unit_to_calories != None):
            #if we have we mutiply servings with the calorie ammount so it can be sent
            ingredient_calories = ingred_unit_cal.ingredient_unit_to_calories*servings
        else:
            #else we send nothing
            ingredient_calories = None
        #we calculate how many ingredients we need
        ingredient_amount = recipe_ingredient.quantity_per_serving*servings
        # we save all the values we need
        ingredient = {"name":ingredient_name,"amount":ingredient_amount,"unit":ingredient_unit,"calories":ingredient_calories}
        #and append it to the structure
        ingredient_structure.append(ingredient)
        #as long as we have a value add it to the sum
        if(ingredient_calories != None):
            #sum without servings
            cal += ingredient_calories/servings
            #sum with servings
            cal_per_serving += ingredient_calories
   
    recipe = {"name":name,"owner":owner,"description":description,"servings":servings,"ingredients":ingredient_structure,"calories":cal,"calories_per_serving":cal_per_serving}
    return recipe
   
@login_required
def create_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            new_user = User.objects.create_user(username=username, password=password)
            new_user = authenticate(username=username, password=password)
            if new_user:
                auth_login(request, new_user)
            return redirect('home')
    else:
        form = UserCreationForm()
 
    return render(request, 'cook_app/create_user.html', {'form': form})
 
#dynamic_form_view is where we add more ingredients dynamically
@login_required
def dynamic_form_view(request):
    IngredientFormSet = formset_factory(RecipeIngredientForm)
    #if we send a post
    if request.method == "POST":
        recipe_form = RecipeForm(request.POST,prefix="recipe")
        ingredient_formset = IngredientFormSet(request.POST,prefix="ingredients")
        if recipe_form.is_valid():
            # create recipe
            recipe_name = recipe_form.cleaned_data["recipe_name"]
            recipe, created = Recipe.objects.get_or_create(title=recipe_name)
            recipe.save()
            # create recipe owner
            user = request.user
            description = recipe_form.cleaned_data["description"]
            recipe_owner = RecipeOwner(description=description, owner=user, recipe=recipe)
            recipe_owner.save()
            # save number of servings
            servings = recipe_form.cleaned_data["servings"]
        if ingredient_formset.is_valid():
            for form in ingredient_formset:
                # create and save the ingredient
                ingredient_name   = form.cleaned_data["ingredient_name"]
                ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
                ingredient.save()
                # create and save the unit
                unit = form.cleaned_data["unit"]
                # get or create unit-cal info on these
                unit_cal, created = IngredientUnitToCal.objects.get_or_create(ingredient = ingredient, unit=unit)
                unit_cal.save()
                # get or create recipe ingredient
                quantity_per_serving = form.cleaned_data["amount"]/servings
                recipeIngredient =  RecipeIngredient(ingredient=ingredient, recipe=recipe, unit=unit, quantity_per_serving=quantity_per_serving)
                recipeIngredient.save()
            return redirect('home')
    else:
        recipe_form = RecipeForm(prefix="recipe")
        ingredient_formset = IngredientFormSet(prefix="ingredients")
    return render(request, 'cook_app/dynamic_form.html', {'recipe_form' : recipe_form , 'ingredient_formset': ingredient_formset})
#shows all the recipes
@login_required
def recipes_view(request):
    #gets all the recipes
    recipes = Recipe.objects.all()
    #sends them to html
    return render(request, 'cook_app/recipes.html', {'recipes' : recipes})
#this is when we click on a recipe from the recipe list
@login_required
def recipe_details(request, pk):
    servings=1
    #post means that we have changed the ammount of servings
    if request.method == "POST":
        serving_form = ServingsForm(request.POST)
        if serving_form.is_valid():
            #you should not be able to have servings be less than 0 so if it is we set it to 1, otherwise we let it be what you wanted it to be
            if(serving_form.cleaned_data['servings'] <= 0):
                servings = 1
            else:
                servings=serving_form.cleaned_data['servings']
        comment_form = CommentForm(request.POST)
        #if we have sent in a correct comment
        if comment_form.is_valid():
            #set the correct values and saves it to the database
            title = comment_form.cleaned_data["title"]
            comment = comment_form.cleaned_data["comment"]
            user = request.user
            recipe = Recipe.objects.get(id=pk)
            date = datetime.datetime.now()
            comment_object = RecipeComment(title=title, comment=comment, recipe=recipe, author=user, published_date=date)
            comment_object.save()
        else:
            print("it's not valid!")
    #gets the structure of the template based on servings
    recipe_structure = get_recipe_structure(pk, servings)
    #gets the commentform
    comment_form = CommentForm()
    #sets the serving forms servings to what you chose or otherwise 1
    serving_form = ServingsForm(initial={'servings': servings})
    #gets all the comments ordered by their publish date
    comments = RecipeComment.objects.filter(recipe__title=recipe_structure["name"]).order_by("published_date")
    return render(request, 'cook_app/recipe_details.html', {"pk":pk,"comments":comments,'comment_form':comment_form,'serving_form':serving_form,"recipe_structure":recipe_structure})
#this is used to get all the recipes that the user has saved
@login_required
def history_view(request):
    #creates a list of all the UserHistory objects that have the same user as the current user
    history = UserHistory.objects.filter(owner=request.user)
    #sends that list to the renderer
    return render(request, 'cook_app/history.html', {"history":history})
 
#this is used to get a list of all Ingredients which units have yet to be defined
@login_required
def ingredient_list(request):
    #gets all the ingredeients that have to calorie count
    ingredients = IngredientUnitToCal.objects.filter(ingredient_unit_to_calories=None)
    return render(request, 'cook_app/ingredient_list.html', {'ingredients' : ingredients})
 
#add_specific_ingredient is where you set the calorie count of an ingredient without a calorie count
@login_required
def add_specific_ingredient(request,pk):
    #get the ingredientUnitToCal based on the pk sent in the url
    ingredient_unit = get_object_or_404(IngredientUnitToCal, pk=pk)
    #set the ingredient name unit and ingredient so we can send it
    ingredient_name = ingredient_unit.ingredient.name
    unit = ingredient_unit.unit.unit
    ingredient = (ingredient_name,unit)
    #if you post it means you have given a calorie count and we should save it to the database
    if request.method == "POST":
        form = SpecificCalorieForm(request.POST)
        if form.is_valid():
            kcal = form.cleaned_data['calories']
            ingredient_unit.initialized = True
            ingredient_unit.ingredient_unit_to_calories = kcal
            ingredient_unit.save()
        return redirect('ingredient_list')
    else:
        form = SpecificCalorieForm(initial={'ingredient_name':ingredient_name,'unit':unit})
    return render(request, 'cook_app/add_specific_ingredient.html', {"form":form, "ingredient":ingredient})
 
#this is used to create a new ingredient that is not (yet) used in a recipe
@login_required
def add_ingredient(request):
    #gets the ammount of uninitialized ingredients
    unlogged_ingredients = IngredientUnitToCal.objects.filter(initialized=False).count()
    saved = False
    if request.method == "POST":
        saved = True
        #if it is valid we create a new ingredient
        form = CalorieForm(request.POST)
        if form.is_valid():
            kcal = form.cleaned_data['calories']
            unit = form.cleaned_data['unit']
            ingredient_name = form.cleaned_data['ingredient_name']
            ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
            ingredient_unit, created = IngredientUnitToCal.objects.get_or_create(ingredient = ingredient, unit=unit)
            ingredient_unit.initialized = True
            ingredient_unit.ingredient_unit_to_calories = kcal
            ingredient_unit.save()
        form = CalorieForm()
    else:
        form = CalorieForm()
    return render(request, 'cook_app/add_ingredient.html', {"form":form, "saved":saved, "unlogged_ingredients":unlogged_ingredients})
 
#this view is used to save a recipe so that you can view it later
@login_required
def save(request, servings, recipe):
    #gets the date and current user
    date = datetime.datetime.now()
    user = request.user
    #gets the recipe from the title
    recipe = get_object_or_404(Recipe,title=recipe)
    #creates the history object
    history, created = UserHistory.objects.get_or_create(
        created_date=date,
        servings=servings,
        owner = user,
        recipe=recipe)
    history.save()
    return redirect('home')
 
#this view is used to see one of your history objects
@login_required
def history_details(request, pk):
    history = get_object_or_404(UserHistory, pk=pk)
    recipe_structure = get_recipe_structure(history.recipe.pk, history.servings)
    created_date = history.created_date
    recipe_structure["created_date"] = created_date
    return render(request, 'cook_app/history_details.html', {"recipe_structure":recipe_structure})
 
 
# resets the database by deleting all things from the database and then populates the database
# with some dummy data to show basic functions of the webapp.
@login_required
def reset_database(request):
    #deletes all the objects
    Unit.objects.all().delete()
    Recipe.objects.all().delete()
    RecipeOwner.objects.all().delete()
    RecipeIngredient.objects.all().delete()
    IngredientUnitToCal.objects.all().delete()
    Ingredient.objects.all().delete()
    #populates the database with units
    units = ["dl","g","pieces","l","teaspoon","pinch","tablespoon","cup"]
    #saves them to the database
    for unit in units:
        unit_model = Unit(unit=unit)
        unit_model.save()
    #creates several ingredients
    ingredients = [
        {"name":"milk","unit":"dl","cal":42},
        {"name":"butter","unit":"g","cal":190},
        {"name":"flour","unit":"dl","cal":30},
        {"name":"sugar","unit":"tablespoon","cal":30},
        {"name":"egg","unit":"pieces","cal":78},
        {"name":"void shard","unit":"pinch","cal":None}
        ]
    #iterates over the ingredients 
    for ingredient in ingredients:
        #saves the ingredient with Model Ingredient
        ingredient_model = Ingredient(name=ingredient["name"])
        ingredient_model.save()
        #gets the unit
        unit = ingredient["unit"]
        #gets the unit object from the database
        unit_model = Unit.objects.get(unit=unit)
        #saves the IngredientUnitToCal
        converter = IngredientUnitToCal(
            ingredient=ingredient_model,
            unit=unit_model,
            ingredient_unit_to_calories=ingredient["cal"]
            )
        converter.save()
    #creates a recipe for a wondeful cookie
    recipe = Recipe(title="Wonderful Cookie")
    recipe.save()
    #iterate three times
    for i in range(0,3):
        #gets a ingredient from the list
        ingredient = ingredients[i]
        #gets the object
        ingredient_model = Ingredient.objects.get(name=ingredient["name"])
        unit = Unit.objects.get(unit=ingredient["unit"])
        amount = i*7+5
        #creates the recipe ingredient
        recipe_ingredient = RecipeIngredient(
            quantity_per_serving=amount,
            recipe=recipe,
            ingredient=ingredient_model,
            unit=unit
            )
        recipe_ingredient.save()
    #creates an owner of the recipe with a comment
    owner = RecipeOwner(
        description="A wonderful cookie, for the entire family",
        recipe = recipe,
        owner = request.user
        )
    owner.save()
    #same thing as above but with a cake
    recipe = Recipe(title="Magnificent Cake")
    recipe.save()
    for i in range(3,6):
        ingredient = ingredients[i]
        ingredient_model = Ingredient.objects.get(name=ingredient["name"])
        unit = Unit.objects.get(unit=ingredient["unit"])
        amount = i*6+8
        recipe_ingredient = RecipeIngredient(
            quantity_per_serving=amount,
            recipe=recipe,
            ingredient=ingredient_model,
            unit=unit
            )
        recipe_ingredient.save()
 
    owner = RecipeOwner(
        description="The most magnificent cake you will ever see!",
        recipe = recipe,
        owner = request.user
        )
    owner.save()
    return redirect('home')