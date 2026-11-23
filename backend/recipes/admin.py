from django.contrib import admin

from .models import (Category, Ingredient, IngredientFeature, Recipe, RecipeItem)


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    fk_name = "recipe"
    extra = 0
    fields = ("ingredient", "amount", "amount_max", "quantity_note", "group", "alternative_group", "is_optional")
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_servings", "owner")
    list_filter = ("category",)
    search_fields = ("name",)
    autocomplete_fields = ("category", "owner")
    inlines = (RecipeItemInline,)


@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount", "quantity_note", "group")
    search_fields = ("recipe__name", "ingredient__canonical_name")
    autocomplete_fields = ("recipe", "ingredient")


@admin.register(IngredientFeature)
class IngredientFeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "kind")
    search_fields = ("name",)
    list_filter = ("kind",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("canonical_name", "base_unit")
    search_fields = ("canonical_name",)
    list_filter = ("base_unit",)
    filter_horizontal = ("features",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "parent")
    autocomplete_fields = ("parent",)
