from django.conf import settings
from django.db import models
from django.db.models import Q


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name="settings")
    default_servings = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(default_servings__gte=1), name="default_servings_positive"),
        ]

    def __str__(self):
        return f"Settings: {self.user}"

class UserFeaturePref(models.Model):
    class Level(models.TextChoices):
        DISLIKE = "dislike", "Dislike"
        AVOID = "avoid", "Avoid"
        ALLERGY = "allergy", "Allergy / Strict"
        PREFER = "prefer", "Prefer"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feature_preferences",
    )
    feature = models.ForeignKey(
        "recipes.IngredientFeature",
        on_delete=models.CASCADE,
        related_name="user_preferences",
    )
    level = models.CharField(max_length=30, choices=Level.choices, default=Level.AVOID)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "feature"], name="unique_user_feature_pref")
        ]
    def __str__(self):
        return f"{self.user}: {self.feature} ({self.level})"
