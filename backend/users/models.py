from django.conf import settings
from django.db import models
from django.db.models import Q

from recipes.models import Allergen, Diet, Ingredient


class UserPreferences(models.Model):
    class MeasurementSystem(models.TextChoices):
        METRIC = "metric", "Metric"
        IMPERIAL = "imperial", "Imperial"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="food_preferences")
    household_size = models.PositiveSmallIntegerField(default=1)
    measurement_system = models.CharField(
        max_length=10, choices=MeasurementSystem.choices, default=MeasurementSystem.METRIC
    )
    allergies = models.ManyToManyField(Allergen, blank=True, related_name="user_preferences")
    required_diets = models.ManyToManyField(Diet, blank=True, related_name="user_preferences")
    excluded_ingredients = models.ManyToManyField(Ingredient, blank=True, related_name="excluded_by_users")
    liked_ingredients = models.ManyToManyField(Ingredient, blank=True, related_name="liked_by_users")
    disliked_ingredients = models.ManyToManyField(Ingredient, blank=True, related_name="disliked_by_users")

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(household_size__gte=1), name="household_size_positive"),
        ]

    def __str__(self):
        return f"Food preferences: {self.user}"
