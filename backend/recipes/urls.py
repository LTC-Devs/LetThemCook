from django.urls import path

from . import api_views

urlpatterns = [
    path("", api_views.recipe_list, name="api_recipe_list"),
    path("suggestions/", api_views.recipe_suggestions, name="api_recipe_suggestions"),
    path("<int:recipe_id>/", api_views.recipe_detail, name="api_recipe_detail"),
]
