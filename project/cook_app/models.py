from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
# Create your models here.
 
#the recipe should only have a title
#it should return its title
class Recipe(models.Model):
    title = models.CharField(max_length=200)
 
    def __str__(self):
        return self.title
 
#RecipeComment is where comments are saved, it will have a title(200 characters), a commment(using text field since it will be reflected in the Textarea widget of the auto-generated form field)
#, an author key that will be linked to the current user, a recipe key and a date of comment
#the return of RecipeComment is the title and the first ten letters of the comment
class RecipeComment(models.Model):
    title = models.CharField(max_length=200)
    comment = models.TextField()
    #sets the author based on model that django gives us named auth
    author = models.ForeignKey('auth.User')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,)
    published_date = models.DateTimeField(
        blank=True,
        null=True)
    def __str__(self):
        return self.title + " " + self.comment[0:10]
 
#UserHistory is how the saved recipes of a user is stored, it stores the date of saved, the ammount of servings the user needed(as an integer field), a foreign key the the person who saved the recipe
#and the recipe itself.
class UserHistory(models.Model):
    created_date = models.DateTimeField()
    servings = models.PositiveIntegerField()
    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,)
 
#RecipeOwner is how we store the owner and description of a recipe, it returns the owner and the recipe
#the recipe stores the description and two foreign keys, one to the owner of the recipe as an auth.User and the other as a key to a recipe
class RecipeOwner(models.Model):
    description = models.TextField()
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,)
    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE)
def __str__(self):
        return self.owner + " " + self.recipe
 
#ingredient is how we store the name of the ingredient, it is mostly used as a key. If returned it will display the name of the ingredient.
#ingredient contains one variable which is a charfield of 50 which will represent the name of the ingredient
class Ingredient(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
#unit is how we store the types of meassurements that exist eg. (ML, CL,DL, gram, pinch), it will return its unit type as a string
#Unit contains one variable which is a charfield of 10 which will represent the type of unit
class Unit(models.Model):
    unit = models.CharField(max_length=10)
    def __str__(self):
        return self.unit
 
#RecipeIngredient is how we store an Ingredient in a recipe, eg.(carrot 4 st), it will return the recipe's name and the ingredient name
#RecipeIngredient contains a decimalField which will tell us how many of a unit type is used in the recipe, a foreign key to the recipe itself, a foreign key to the ingredient and the unit which the ingredient uses.
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
 
#IngredientUnitToCal is how we store how many calories an Ingredient contains based on the unit type, eg.(true carrot  4 st) it will return an array of the ingredient name, the unit type and if it is initialized
#IngredientUnitToCal contains initialized which tells us if we have given the model all its values, ingredient_unit_to_calories which tells us how many calories the ingredient has based
#on unit type and then two foreign keys to the ingredient and the unit
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
