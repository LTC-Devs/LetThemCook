from django.contrib import admin

from .models import UserPreferences


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "household_size", "measurement_system")
    search_fields = ("user__username",)
    filter_horizontal = ("allergies", "required_diets", "excluded_ingredients", "liked_ingredients", "disliked_ingredients")
