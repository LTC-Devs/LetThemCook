from django.contrib import admin

from .models import PantryItem


@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    list_display = ("user", "ingredient", "product", "manual_name", "quantity", "unit", "expiry_date", "status")
    list_filter = ("status", "expiry_date")
    search_fields = ("manual_name", "ingredient__name", "product__name", "user__username")
    autocomplete_fields = ("user", "ingredient", "product")
