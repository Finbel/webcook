from .forms import RecipeIngredientForm, RecipeForm, CalorieForm, ServingsForm, CommentForm, SpecificCalorieForm
from .models import Recipe, Ingredient, RecipeIngredient, Unit, RecipeOwner, IngredientUnitToCal, UserHistory, RecipeComment
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

class BaseArticleFormSet(BaseFormSet):
	def add_fields(self, form, index):
		super(BaseArticleFormSet, self).add_fields(form, index)
		form.fields["my_field"] = forms.CharField()

# Create your views here.
def home(request):
	return render(request, 'cook_app/home.html', {})

def get_recipe_structure(recipe_pk, servings):
	recipe = Recipe.objects.get(id=recipe_pk)
	name = recipe.title
	owner = RecipeOwner.objects.get(recipe__id=recipe_pk).owner.username
	ingredient_structure = []

	recipe_ingredients = RecipeIngredient.objects.filter(recipe__id=recipe_pk)

	ingredient_tuples = []
	for recipe_ingredient in recipe_ingredients:
		converter = IngredientUnitToCal.objects.get(ingredient=recipe_ingredient.ingredient, unit=recipe_ingredient.unit)		
		ingredient_tuples.append((recipe_ingredient,converter))

	cal = 0
	cal_per_serving = 0
	for ingredient_tuple in ingredient_tuples:
		recipe_ingredient = ingredient_tuple[0]
		ingred_unit_cal = ingredient_tuple[1]
		ingredient_name = recipe_ingredient.ingredient.name
		ingredient_unit = recipe_ingredient.unit.unit
		if(ingred_unit_cal.ingredient_unit_to_calories != None):
			ingredient_calories = ingred_unit_cal.ingredient_unit_to_calories*servings
		else:
			ingredient_calories = None
		ingredient_amount = recipe_ingredient.quantity_per_serving*servings
		ingredient = {"name":ingredient_name,"amount":ingredient_amount,"unit":ingredient_unit,"calories":ingredient_calories}
		ingredient_structure.append(ingredient)
		if(ingredient_calories != None):
			cal += ingredient_calories/servings
			cal_per_serving += ingredient_calories 
	
	recipe = {"name":name,"owner":owner,"servings":servings,"ingredients":ingredient_structure,"calories":cal,"calories_per_serving":cal_per_serving}
	return recipe
	
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

def dynamic_form_view(request):
	IngredientFormSet = formset_factory(RecipeIngredientForm)
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

def recipes_view(request):
	recipes = Recipe.objects.all()
	return render(request, 'cook_app/recipes.html', {'recipes' : recipes})

def recipe_details(request, pk):
	servings=1
	if request.method == "POST":
		serving_form = ServingsForm(request.POST)
		if serving_form.is_valid():
			if(serving_form.cleaned_data['servings'] <= 0):
				servings = 1
			else:
				servings=serving_form.cleaned_data['servings']
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
			title = comment_form.cleaned_data["title"]
			comment = comment_form.cleaned_data["comment"]
			user = request.user
			recipe = Recipe.objects.get(id=pk)
			date = datetime.datetime.now()
			comment_object = RecipeComment(title=title, comment=comment, recipe=recipe, author=user, published_date=date)
			comment_object.save()
		else:
			print("it's not valid!")
	recipe_structure = get_recipe_structure(pk, servings) 
	comment_form = CommentForm()
	serving_form = ServingsForm(initial={'servings': servings})

	comments = RecipeComment.objects.filter(recipe__title=recipe_structure["name"]).order_by("published_date")
	return render(request, 'cook_app/recipe_details.html', {"pk":pk,"comments":comments,'comment_form':comment_form,'serving_form':serving_form,"recipe_structure":recipe_structure})

def history_view(request):
	history = UserHistory.objects.filter(owner=request.user)
	return render(request, 'cook_app/history.html', {"history":history})

def ingredient_list(request):
	ingredients = IngredientUnitToCal.objects.filter(ingredient_unit_to_calories=None)
	return render(request, 'cook_app/ingredient_list.html', {'ingredients' : ingredients})

def add_specific_ingredient(request,pk):
	ingredient_unit = get_object_or_404(IngredientUnitToCal, pk=pk)
	ingredient_name = ingredient_unit.ingredient.name
	unit = ingredient_unit.unit.unit
	ingredient = (ingredient_name,unit)
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

def add_ingredient(request):
	unlogged_ingredients = IngredientUnitToCal.objects.filter(initialized=False).count()
	saved = False
	if request.method == "POST":
		saved = True
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


def save(request, servings, recipe):
	date = datetime.datetime.now()
	user = request.user
	recipe = get_object_or_404(Recipe,title=recipe)
	history, created = UserHistory.objects.get_or_create(
		created_date=date,
		servings=servings,
		owner = user,
		recipe=recipe)
	history.save()
	return redirect('home')

def history_details(request, pk):
	history = get_object_or_404(UserHistory, pk=pk)
	recipe_structure = get_recipe_structure(history.recipe.pk, history.servings)
	created_date = history.created_date
	recipe_structure["created_date"] = created_date
	return render(request, 'cook_app/history_details.html', {"recipe_structure":recipe_structure})

def reset_database(request):
	
	Unit.objects.all().delete()
	Recipe.objects.all().delete()
	RecipeOwner.objects.all().delete()
	RecipeIngredient.objects.all().delete()
	IngredientUnitToCal.objects.all().delete()
	Ingredient.objects.all().delete()

	units = ["dl","g","pieces","l","teaspoon","pinch","tablespoon","cup"]

	for unit in units:
		unit_model = Unit(unit=unit) 
		unit_model.save()

	ingredients = [
		{"name":"milk","unit":"dl","cal":42},
		{"name":"butter","unit":"g","cal":190},
		{"name":"flour","unit":"dl","cal":30},
		{"name":"sugar","unit":"tablespoon","cal":30},
		{"name":"egg","unit":"pieces","cal":78},
		{"name":"void shard","unit":"pinch","cal":None}
		]

	for ingredient in ingredients:
		ingredient_model = Ingredient(name=ingredient["name"])
		ingredient_model.save()
		unit = ingredient["unit"]
		unit_model = Unit.objects.get(unit=unit)
		converter = IngredientUnitToCal(
			ingredient=ingredient_model,
			unit=unit_model,
			ingredient_unit_to_calories=ingredient["cal"]
			)
		converter.save()

	recipe = Recipe(title="Wonderful Cookie")
	recipe.save()
	for i in range(0,3):
		ingredient = ingredients[i]
		ingredient_model = Ingredient.objects.get(name=ingredient["name"])
		unit = Unit.objects.get(unit=ingredient["unit"])
		amount = i*7+5
		recipe_ingredient = RecipeIngredient(
			quantity_per_serving=amount,
			recipe=recipe,
			ingredient=ingredient_model,
			unit=unit
			)
		recipe_ingredient.save()

	owner = RecipeOwner(
		description="A wonderful cookie, for the entire family",
		recipe = recipe,
		owner = request.user
		)
	owner.save()

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
		description="It takes the cake, it takes the cake I tell you!",
		recipe = recipe,
		owner = request.user
		)
	owner.save()
	return redirect('home')