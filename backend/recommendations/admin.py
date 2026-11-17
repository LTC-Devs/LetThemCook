from django.contrib import admin

from .models import CookingHistory, MealPlan, PlannedMeal, RecipeFeedback


class PlannedMealInline(admin.TabularInline):
    model = PlannedMeal
    extra = 0
    autocomplete_fields = ("recipe",)


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "start_date", "end_date")
    search_fields = ("title", "user__username")
    list_filter = ("start_date",)
    autocomplete_fields = ("user",)
    inlines = (PlannedMealInline,)


@admin.register(RecipeFeedback)
class RecipeFeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "value", "updated_at")
    list_filter = ("value",)
    autocomplete_fields = ("user", "recipe")


@admin.register(CookingHistory)
class CookingHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "cooked_at", "servings")
    autocomplete_fields = ("user", "recipe")
