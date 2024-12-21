from django.shortcuts import render
from .serializers import IngredientSerializer,RecipeIngredientSerializer, RecipeSerializer
from .models import Ingredient,Recipe, RecipeIngredient
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
print(base_dir)
class IngredientView(APIView):
    def get(self, request):
        """Retrieve all available ingredients."""
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data  
            for item in data:
                name = item.get("name")
                unit = item.get("unit")
                quantity = item.get("quantity")
                
                if not all([name, unit, quantity]):
                    return Response({"error": "Missing fields in input data"}, status=400)
                
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    unit=unit,
                    defaults={"quantity": quantity}
                )
                
                if not created:
                    ingredient.quantity = quantity
                    ingredient.save()
            
            return Response({"message": "Ingredients updated successfully!"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class IngredientUpdateView(APIView):
    """Handles updating quantities after cooking."""

    def patch(self, request, pk):
        """Decrease ingredient quantities."""
        try:
            ingredient = Ingredient.objects.get(pk=pk)
        except Ingredient.DoesNotExist:
            return Response({"error": "Ingredient not found."}, status=status.HTTP_404_NOT_FOUND)

        quantity_used = request.data.get('quantity_used')
        if not quantity_used or quantity_used <= 0:
            return Response({"error": "Quantity used must be a positive number."}, status=status.HTTP_400_BAD_REQUEST)

        if ingredient.quantity < quantity_used:
            return Response({"error": "Insufficient quantity available."}, status=status.HTTP_400_BAD_REQUEST)

        ingredient.quantity -= quantity_used
        ingredient.save()

        return Response({"message": f"{quantity_used} {ingredient.unit} of {ingredient.name} used."}, status=status.HTTP_200_OK)


import os

class RecipeCreateView(APIView):
    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description', '')
        instructions = request.data.get('instructions', '')
        is_sweet = request.data.get('is_sweet', False)
        dish_type = request.data.get('dish_type', '')
        ingredients = request.data.get('ingredients', [])

        if not title or not ingredients:
            return Response({"error": "Title and ingredients are required!"}, status=status.HTTP_400_BAD_REQUEST)
        recipe_details = f"Title: {title}\n"
        recipe_details += f"Description: {description}\n"
        recipe_details += f"Instructions: {instructions}\n"
        recipe_details += f"Dish Type: {dish_type}\n"
        recipe_details += f"Sweets: {'Yes' if is_sweet else 'No'}\n"
        
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_name = ingredient.get('name', 'Unknown Ingredient')
            quantity = ingredient.get('quantity', 'N/A')
            unit = ingredient.get('unit', 'unit')
            ingredient_list.append(f"{ingredient_name} ({quantity} {unit})")
        
        recipe_details += "Ingredients: " + ", ".join(ingredient_list) + "\n"
        recipe_details += "\n"
        file_path = os.path.join(base_dir, 'my_fav_recipes.txt')

        try:
            with open(file_path, 'a') as file:
                file.write(recipe_details)
            
            return Response({
                "message": "Recipe created and saved to file successfully!",
                "recipe": recipe_details
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def load_recipes():
    recipes = []
    with open(os.path.join(base_dir, 'my_fav_recipes.txt'), 'r') as file:
        data = file.read().strip().split("\n\n")
        for recipe_data in data:
            recipe = {}
            lines = recipe_data.split("\n")
            recipe['title'] = lines[0].split(":")[1].strip()
            recipe['description'] = lines[1].split(":")[1].strip()
            recipe['instructions'] = lines[2].split(":")[1].strip()
            recipe['dish_type'] = lines[3].split(":")[1].strip()
            recipe['sweets'] = True if "Yes" in lines[4] else False
            recipe['ingredients'] = [ingredient.strip() for ingredient in lines[5].split(":")[1].split(",")]
            recipes.append(recipe)
    return recipes

def recommend_recipes(preferences, available_ingredients):
    recipes = load_recipes()
    recommended = []
    for recipe in recipes:
        if preferences.get("sweet") and not recipe['sweets']:
            continue
        
        if all(ingredient in recipe['ingredients'] for ingredient in available_ingredients):
            recommended.append(recipe)
    
    return recommended

import json
class ChatbotInteractionView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            user_input = json.loads(request.body)
            preferences = user_input.get("preferences", {})
            available_ingredients = user_input.get("ingredients", [])

            if not preferences or not available_ingredients:
                return Response({"error": "Preferences and ingredients are required!"}, status=status.HTTP_400_BAD_REQUEST)
            recommended_recipes = recommend_recipes(preferences, available_ingredients)

            if not recommended_recipes:
                return Response({"message": "No recipes match your preferences and ingredients."}, status=status.HTTP_200_OK)

            return Response({"recommended_recipes": recommended_recipes}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)