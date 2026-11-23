from django.urls import path

from . import api_views

urlpatterns = [
    path('', api_views.pantry_list_create, name='pantry_list_create'),
    path('ingredients/', api_views.pantry_ingredients, name='pantry_ingredients'),
    path('<int:item_id>/', api_views.pantry_item_detail, name='pantry_item_detail'),
]
