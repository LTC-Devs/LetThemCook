"""Structured cookbook data, assuming that raw OCR has been verified."""
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Category(models.Model):
    """Hierarchical chapter/subchapter taxonomy from the book."""
    name = models.CharField(max_length=200, db_index=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )

    class Meta:
            constraints = [
                models.CheckConstraint(
                    condition=~models.Q(parent=models.F('id')),
                    name='prevent_self_parent'
                )
            ]

    def __str__(self):
        return self.name

class IngredientFeature(models.Model):
    class Kind(models.TextChoices):
        ALLERGEN = "allergen", "Allergen"
        DIET = "diet", "Diet"
    name = models.CharField(max_length=150, unique=True)
    kind = models.CharField(max_length=50, choices=Kind.choices, default=Kind.ALLERGEN)
    def __str__(self):
        return f"{self.name} ({self.kind})"

class BaseUnit(models.TextChoices):
    GRAM = "g", "g"
    MILLILITER = "ml", "ml"
    PIECE = "pcs", "szt."

class Ingredient(models.Model):
    """Canonical ingredient; never create one from unreviewed OCR blindly."""
    canonical_name = models.CharField(max_length=200, unique=True)
    base_unit = models.CharField(max_length=30, choices=BaseUnit.choices, help_text="e.g. g, ml, pcs")
    features = models.ManyToManyField(
        IngredientFeature, related_name="ingredients", blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(base_unit__in=BaseUnit.values), name="ingredient_base_unit_valid"),
        ]

    def __str__(self):
        return f"{self.canonical_name} [{self.base_unit}]"

class Recipe(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name="custom_recipes", help_text="Set for a user-created recipe; blank for public book recipes.",
    )
    name = models.CharField(max_length=300, db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes"
    )
    base_servings = models.PositiveSmallIntegerField(null=True, blank=True)
    steps = models.JSONField(default=list, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(base_servings__gte=1) | Q(base_servings__isnull=True), name="recipe_base_servings_positive"),
        ]

    def __str__(self):
        return self.name


class RecipeItem(models.Model):
    """One ingredient of a recipe; amounts are in the ingredient's base unit.

    A source line can hold alternatives/ranges, e.g. '2-3 łyżki masła lub oleju': one item per
    ingredient, sharing an alternative_group, with the book's measure ('2-3 łyżki') in quantity_note.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="items")
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="recipe_items"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, help_text="Empty for 'sól do smaku', expressed in ingredient.base_unit")
    amount_max = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, help_text="Upper range end (np. 4-5 łyżek)")
    quantity_note = models.CharField(max_length=150, blank=True, help_text="the book's measure, e.g. 2-3 łyżki, do smaku")
    group = models.CharField(max_length=150, blank=True, help_text="e.g. sos musztardowy")
    alternative_group = models.CharField(max_length=150, blank=True, help_text="group of interchangeable items")
    is_optional = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gte=0) | Q(amount__isnull=True), name="recipe_item_amount_nonneg"),
            models.CheckConstraint(condition=Q(amount_max__gte=0) | Q(amount_max__isnull=True), name="recipe_item_max_nonneg"),
            models.CheckConstraint(
                condition=Q(amount_max__isnull=True) | Q(amount__isnull=True) | Q(amount_max__gte=F("amount")),
                name="recipe_item_range_order",
            ),
        ]

    def __str__(self):
        return f"{self.quantity_note or self.amount or ''} {self.ingredient.canonical_name}".strip()
