from django import forms
from .models import Unit

class RecipeForm(forms.Form):
	recipe_name = forms.CharField()
	servings = forms.IntegerField()
	description = forms.CharField(widget=forms.Textarea)

class RecipeIngredientForm(forms.Form):
	ingredient_name = forms.CharField()
	unit = forms.ModelChoiceField(queryset=Unit.objects.all())
	amount = forms.DecimalField()

class SpecificCalorieForm(forms.Form):
	ingredient_name = forms.CharField(widget=forms.HiddenInput())
	unit = forms.CharField(widget=forms.HiddenInput())
	calories = forms.DecimalField()

class CalorieForm(forms.Form):
	ingredient_name = forms.CharField()
	unit = forms.ModelChoiceField(queryset=Unit.objects.all())
	calories = forms.DecimalField()

class ServingsForm(forms.Form):
	servings = forms.IntegerField()

class CommentForm(forms.Form):
	title = forms.CharField()
	comment = forms.CharField(widget=forms.Textarea)