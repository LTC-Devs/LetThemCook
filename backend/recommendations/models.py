from django.conf import settings
from django.db import models
from django.db.models import Q


class RecipeFeedback(models.Model):
    class Value(models.IntegerChoices):
        DISLIKE = -1, "Disliked"
        LIKE = 1, "Liked"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipe_feedback")
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.CASCADE, related_name="feedback")
    value = models.SmallIntegerField(choices=Value.choices)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_user_recipe_feedback"),
            models.CheckConstraint(condition=Q(value__in=[-1, 1]), name="feedback_value_valid"),
        ]

    def __str__(self):
        return f"{self.user}: {self.recipe} ({self.value})"


class CookingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cooking_history")
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.PROTECT, related_name="cooking_history")
    cooked_at = models.DateTimeField()
    servings = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-cooked_at"]

    def __str__(self):
        return f"{self.recipe}: {self.cooked_at:%Y-%m-%d}"


class MealPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meal_plans")
    title = models.CharField(max_length=200, default="Meal plan")
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(end_date__gte=models.F("start_date")), name="mealplan_valid_date_range")]

    def __str__(self):
        return self.title


class PlannedMeal(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        DINNER = "dinner", "Dinner"
        SNACK = "snack", "Snack"
        OTHER = "other", "Other"

    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="meals")
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.PROTECT, related_name="planned_meals")
    planned_for = models.DateField()
    meal_type = models.CharField(max_length=12, choices=MealType.choices, default=MealType.OTHER)
    servings = models.PositiveSmallIntegerField(default=1)
    cooked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["planned_for", "id"]
        constraints = [
            models.CheckConstraint(condition=Q(servings__gte=1), name="planned_servings_positive"),
        ]

    def __str__(self):
        return f"{self.recipe}: {self.planned_for}"
