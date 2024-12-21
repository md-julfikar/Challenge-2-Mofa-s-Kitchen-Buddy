from django.urls import path
from .views import IngredientView, IngredientUpdateView, RecipeCreateView
urlpatterns = [
    path('ingredients/',IngredientView.as_view(),name='ingredient-created'),
    path('ingredients/<int:pk>/', IngredientUpdateView.as_view(), name='ingredient-update'),
    path("recipes/", RecipeCreateView.as_view(), name='recipe-create'),
]