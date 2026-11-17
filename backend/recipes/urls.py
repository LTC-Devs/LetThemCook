from django.urls import path

from . import api_views

urlpatterns = [
    path("", api_views.recipe_list, name="api_recipe_list"),
    path("<int:recipe_id>/", api_views.recipe_detail, name="api_recipe_detail"),
]
