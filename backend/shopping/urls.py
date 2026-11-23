from django.urls import path
from . import views

urlpatterns = [
    path('', views.shopping_list_view, name='shopping_list'),
    path('plan/', views.plan_recipe_view, name='shopping_plan_recipe'),
    path('purchase/', views.purchase_view, name='shopping_purchase'),
]
