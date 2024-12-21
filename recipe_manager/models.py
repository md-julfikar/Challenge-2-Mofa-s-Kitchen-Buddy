from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.FloatField()  
    unit = models.CharField(max_length=20)  
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    is_sweet = models.BooleanField(default=False)
    dish_type = models.CharField(max_length=50)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipe_ingredients")
    quantity = models.FloatField() 
    unit = models.CharField(max_length=20) 

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name} for {self.recipe.name}"
