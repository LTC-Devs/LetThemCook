from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("full_name", "ean", "ingredient", "package_amount", "normalised_amount")
    search_fields = ("full_name", "ean", "ingredient__canonical_name")
    autocomplete_fields = ("ingredient",)
