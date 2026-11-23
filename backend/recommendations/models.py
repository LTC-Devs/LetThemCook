import pghistory

from django.conf import settings
from django.db import models
from django.db.models import Q

class RecipeRating(models.Model):
    class Value(models.IntegerChoices):
        DISLIKE = -1, "Dislike"
        LIKE = 1, "Like"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipe_ratings")
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.CASCADE, related_name="ratings")
    # TODO: agree on rating version
    rating = models.SmallIntegerField(choices=Value.choices, help_text="Numeric rating like/dislike, -1/1")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_user_recipe_rating"),
            models.CheckConstraint(condition=Q(rating__in=[-1, 1]), name="recipe_rating_like_or_dislike"),
        ]
    def __str__(self):
        return f"{self.user} rated {self.recipe}: {self.rating}"

@pghistory.track(fields=["status"])
class PlannedMeal(models.Model):
    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        PLANNED = "planned", "Planned"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="planned_meals")
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.CASCADE, related_name="planned_meals")
    servings = models.PositiveSmallIntegerField(
        default=1, help_text="Planned portions; filled from UserSettings.default_servings on creation"
    )
    planned_for = models.DateField()
    proposed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED, db_index=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(servings__gte=1), name="planned_meal_servings_positive"),
        ]

    def __str__(self):
        return f"{self.user}: {self.recipe} on {self.planned_for} ({self.status})"
