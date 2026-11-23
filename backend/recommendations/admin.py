from django.contrib import admin

from .models import PlannedMeal, RecipeRating


@admin.register(PlannedMeal)
class PlannedMealAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "planned_for", "servings", "status", "proposed_at")
    list_filter = ("status", "planned_for")
    search_fields = ("user__username", "recipe__name")
    autocomplete_fields = ("user", "recipe")


@admin.register(RecipeRating)
class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "rating")
    list_filter = ("rating",)
    search_fields = ("user__username", "recipe__name")
    autocomplete_fields = ("user", "recipe")
