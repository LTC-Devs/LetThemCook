from django.contrib import admin

from .models import ShoppingList, ShoppingListItem


class ShoppingListItemInline(admin.TabularInline):
    model = ShoppingListItem
    extra = 0
    autocomplete_fields = ("ingredient", "product", "source_recipe_item")


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "meal_plan", "created_at")
    autocomplete_fields = ("user", "meal_plan")
    inlines = (ShoppingListItemInline,)
