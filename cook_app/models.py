from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
# Create your models here.

class Recipe(models.Model):
	title = models.CharField(max_length=200)

	def __str__(self):
		return self.title


class RecipeComment(models.Model):
	title = models.CharField(max_length=200)
	comment	= models.TextField()
	author = models.ForeignKey('auth.User')
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,)
	published_date = models.DateTimeField(
		blank=True, 
		null=True)

	def publish(self):
		self.published_date = timezone.now()
		self.save()

	def __str__(self):
		return self.title + " " + self.comment[0:10]

class UserHistory(models.Model):
	created_date = models.DateTimeField()
	servings = models.PositiveIntegerField()
	owner = models.ForeignKey(
		'auth.User',
		on_delete=models.CASCADE)
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,)

class RecipeOwner(models.Model):
	description	= models.TextField()
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,)
	owner = models.ForeignKey(
		'auth.User',
		on_delete=models.CASCADE)
def __str__(self):
		return self.owner + " " + self.recipe

class Ingredient(models.Model):
	name = models.CharField(max_length=50)
	def __str__(self):
		return self.name

class Unit(models.Model):
	unit = models.CharField(max_length=10)
	def __str__(self):
		return self.unit

class RecipeIngredient(models.Model):
	quantity_per_serving = models.DecimalField(decimal_places=5, max_digits=10, validators=[MinValueValidator(Decimal('0.01'))])
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,)
	ingredient = models.ForeignKey(
		Ingredient,
		on_delete=models.CASCADE)
	unit = models.ForeignKey(
		Unit)
	def __str__(self):
		return self.recipe.title + " " + self.ingredient.name

class IngredientUnitToCal(models.Model):
	initialized = models.BooleanField(default=False);
	ingredient_unit_to_calories = models.DecimalField(decimal_places=5, max_digits=10,null=True,validators=[MinValueValidator(Decimal('0.01'))])
	ingredient = models.ForeignKey(
		Ingredient,
		on_delete=models.CASCADE)
	unit = models.ForeignKey(
		Unit)
	def __str__(self):
		return "[" + self.ingredient.name + " " + self.unit.unit + " " + str(self.initialized) + "]" 
