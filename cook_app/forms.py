from django import forms
from .models import Unit
#these are the forms that are used in the views and given to the template
 
#RecipeForm is used for the creation of the recipe and as such it will take in the three variables which are needed to make a recipe
#recipe_name to give the recipe a name and description for the recipeOwner
#the serving is used to display how many ingredients are going to be needed, and will multiply itself with all the quanteties of the recipe to give them the correct values.
class RecipeForm(forms.Form):
    recipe_name = forms.CharField()
    servings = forms.IntegerField()
    description = forms.CharField(widget=forms.Textarea)
#RecipeIngredientForm is used in combination with the dynamic view so that you can store several ingredients with their ingredient name, unit and amount. using this form we can build a single RecipeIngredient, using dyanic forms we can
#ingredient_name is used to create the model Ingredient
#unit is used to create the model for model Unit
#amount is used to create the model for RecipeIngredient using the previous variables we can get the keys
class RecipeIngredientForm(forms.Form):
    ingredient_name = forms.CharField()
    unit = forms.ModelChoiceField(queryset=Unit.objects.all())
    amount = forms.DecimalField()
 
#SpecificCalorieForm is used in order to give an ingredient with a specific unit a calorie count
#it takes the ingredient name
#the unit type
#creates the model IngredientUnitToCal with the calories
class SpecificCalorieForm(forms.Form):
    ingredient_name = forms.CharField(widget=forms.HiddenInput())
    unit = forms.CharField(widget=forms.HiddenInput())
    calories = forms.DecimalField()
 
# Calori form is used to make a general calorie form where the user
# can decide what name and unit it should have
class CalorieForm(forms.Form):
    ingredient_name = forms.CharField()
    unit = forms.ModelChoiceField(queryset=Unit.objects.all())
    calories = forms.DecimalField()

#ServingsForm is used to tell backened how many servings we are going to make
class ServingsForm(forms.Form):
    servings = forms.IntegerField()
 
#comment form is to make a comment, it has two textfields for title and comment so that we can properly make a Comment object for the database
class CommentForm(forms.Form):
    title = forms.CharField()
    comment = forms.CharField(widget=forms.Textarea)