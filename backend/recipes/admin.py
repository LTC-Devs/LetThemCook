from django.contrib import admin

from .models import (Allergen, Category, Cookbook, Diet, DietCategory,
                     Ingredient, Recipe, RecipeItem, Substitution)


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    fk_name = "recipe"
    extra = 0
    fields = ("position", "raw_text", "ingredient", "sub_recipe", "amount", "amount_max", "unit", "is_optional")
    autocomplete_fields = ("ingredient", "sub_recipe")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "source_number", "cookbook", "category", "parsing_status", "owner")
    list_filter = ("parsing_status", "cookbook", "category")
    search_fields = ("title", "instructions")
    autocomplete_fields = ("cookbook", "category", "owner")
    filter_horizontal = ("diets",)
    inlines = (RecipeItemInline,)


@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    list_display = ("recipe", "position", "ingredient", "raw_text")
    search_fields = ("raw_text", "recipe__title", "ingredient__name")
    autocomplete_fields = ("recipe", "ingredient", "sub_recipe")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    filter_horizontal = ("allergens", "diet_categories")


@admin.register(Cookbook)
class CookbookAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("title", "edition_year", "publisher")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "parent")
    autocomplete_fields = ("parent",)


@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    filter_horizontal = ("excluded_categories",)


@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "substitute", "ratio")
    autocomplete_fields = ("ingredient", "substitute")


for model in [Allergen, DietCategory]:
    admin.site.register(model)
