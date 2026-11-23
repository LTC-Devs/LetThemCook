from django.urls import path

from .demo_api import ranked_recipes

urlpatterns = [
    path('', ranked_recipes, name='api_ranked_recipes'),
]
