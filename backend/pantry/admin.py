from django.contrib import admin

from .models import PantryItem


@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "amount", "status", "expires_at", "added_at")
    list_filter = ("status", "expires_at")
    search_fields = ("product__full_name", "product__ean", "user__username")
    autocomplete_fields = ("user", "product")
