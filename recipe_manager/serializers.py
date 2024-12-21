from rest_framework import serializers
from .models import Ingredient,Recipe, RecipeIngredient

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'unit', 'updated_at']
class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit']

class RecipeSerializer(serializers.ModelSerializer):
    recipe_ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'instructions', 'is_sweet', 'dish_type', 'created_at', 'recipe_ingredients']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        
        return recipe
