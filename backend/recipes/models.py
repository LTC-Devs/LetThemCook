"""Structured cookbook data, without assuming that raw OCR has been verified."""
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Cookbook(models.Model):
    """cookbook edition, a source shared by all recipes"""
    title = models.CharField(max_length=250)
    edition_year = models.PositiveSmallIntegerField()
    publisher = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["title", "edition_year"], name="unique_cookbook_edition"),
        ]

    def __str__(self):
        return f"{self.title} ({self.edition_year})"


class Category(models.Model):
    """Hierarchical chapter/subchapter taxonomy from the book."""
    name = models.CharField(max_length=200, db_index=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )

    def clean(self):
        super().clean()
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({"parent": "A category cannot be its own parent."})

    def __str__(self):
        return self.name


class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class DietCategory(models.Model):
    """Ingredient traits such as meat, fish, dairy or eggs (not dietary labels)."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Diet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    excluded_categories = models.ManyToManyField(DietCategory, blank=True, related_name="excluding_diets")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Canonical ingredient; never create one from unreviewed OCR blindly."""
    name = models.CharField(max_length=200, unique=True)
    aliases = models.JSONField(default=list, blank=True)
    allergens = models.ManyToManyField(Allergen, blank=True, related_name="ingredients")
    diet_categories = models.ManyToManyField(DietCategory, blank=True, related_name="ingredients")

    def __str__(self):
        return self.name


class Substitution(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="substitutions")
    substitute = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="substitute_for")
    ratio = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("1.0000"))
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["ingredient", "substitute"], name="unique_ingredient_substitute"),
            models.CheckConstraint(condition=Q(ratio__gt=0), name="substitution_ratio_positive"),
            models.CheckConstraint(condition=~Q(ingredient=F("substitute")), name="substitution_not_self"),
        ]

    def clean(self):
        super().clean()
        if self.ingredient_id and self.ingredient_id == self.substitute_id:
            raise ValidationError({"substitute": "An ingredient cannot replace itself."})

    def __str__(self):
        return f"{self.ingredient} -> {self.substitute} (x{self.ratio})"


class Recipe(models.Model):
    class ParsingStatus(models.TextChoices):
        RAW = "raw", "Unreviewed OCR"
        REVIEW = "review", "Needs review"
        VERIFIED = "verified", "Verified"

    title = models.CharField(max_length=300, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="recipes")
    cookbook = models.ForeignKey(Cookbook, on_delete=models.PROTECT, null=True, blank=True, related_name="recipes")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name="custom_recipes", help_text="Set for a user-created recipe; blank for public book recipes.",
    )
    source_number = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    source_page = models.PositiveIntegerField(null=True, blank=True)
    servings = models.PositiveSmallIntegerField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    steps = models.JSONField(default=list, blank=True)
    raw_ingredients = models.JSONField(default=list, blank=True)
    review_notes = models.JSONField(default=list, blank=True)
    parsing_status = models.CharField(
        max_length=10, choices=ParsingStatus.choices, default=ParsingStatus.RAW, db_index=True
    )
    # Labels must be manually verified; absence of a tag is NOT proof of suitability.
    diets = models.ManyToManyField(Diet, blank=True, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["cookbook", "source_number"], name="recipe_book_number_idx")]
        constraints = [
            models.CheckConstraint(condition=Q(servings__gte=1) | Q(servings__isnull=True), name="recipe_servings_positive"),
        ]

    def __str__(self):
        return self.title


class RecipeItem(models.Model):
    """An ordered line in a recipe, including a not-yet-parsed ingredient.

    A source line can hold alternatives/ranges, e.g. '2-3 łyżki masła lub oleju'.
    Until reviewed, preserve that entire line in raw_text and leave ingredient blank.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="items")
    position = models.PositiveIntegerField(default=0)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, null=True, blank=True, related_name="recipe_items"
    )
    sub_recipe = models.ForeignKey(
        Recipe, on_delete=models.PROTECT, null=True, blank=True, related_name="used_as_ingredient_in"
    )
    raw_text = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    amount_max = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=40, blank=True)
    comment = models.TextField(blank=True)
    is_optional = models.BooleanField(default=False)
    substitution_allowed = models.BooleanField(default=True)

    class Meta:
        ordering = ["position", "id"]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gte=0) | Q(amount__isnull=True), name="recipe_item_amount_nonneg"),
            models.CheckConstraint(condition=Q(amount_max__gte=0) | Q(amount_max__isnull=True), name="recipe_item_max_nonneg"),
            models.CheckConstraint(
                condition=Q(amount_max__isnull=True) | Q(amount__isnull=True) | Q(amount_max__gte=F("amount")),
                name="recipe_item_range_order",
            ),
            models.CheckConstraint(condition=Q(ingredient__isnull=True) | Q(sub_recipe__isnull=True), name="recipe_item_one_reference"),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if not (self.ingredient_id or self.sub_recipe_id or self.raw_text.strip()):
            errors["raw_text"] = "Provide a raw line, ingredient, or sub-recipe."
        if self.ingredient_id and self.sub_recipe_id:
            errors["ingredient"] = "Use an ingredient OR a sub-recipe."
        if self.sub_recipe_id and self.recipe_id == self.sub_recipe_id:
            errors["sub_recipe"] = "A recipe cannot contain itself."
        if self.amount is not None and self.amount_max is not None and self.amount_max < self.amount:
            errors["amount_max"] = "Maximum cannot be smaller than minimum."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.raw_text or str(self.ingredient or self.sub_recipe)
