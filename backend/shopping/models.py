from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class ShoppingList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shopping_lists")
    title = models.CharField(max_length=200, default="Shopping list")
    meal_plan = models.ForeignKey(
        "recommendations.MealPlan", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="shopping_lists",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name="items")
    ingredient = models.ForeignKey(
        "recipes.Ingredient", null=True, blank=True, on_delete=models.PROTECT, related_name="shopping_items"
    )
    product = models.ForeignKey(
        "products.Product", null=True, blank=True, on_delete=models.SET_NULL, related_name="shopping_items"
    )
    source_recipe_item = models.ForeignKey(
        "recipes.RecipeItem", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="shopping_items",
    )
    manual_name = models.CharField(max_length=250, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=40, blank=True)
    position = models.PositiveIntegerField(default=0)
    is_checked = models.BooleanField(default=False)
    checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "id"]
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gte=0) | Q(quantity__isnull=True), name="shopping_quantity_nonneg")
        ]

    def clean(self):
        super().clean()
        if not (self.ingredient_id or self.product_id or self.manual_name.strip()):
            raise ValidationError({"manual_name": "Provide an ingredient, product, or manual name."})

    def __str__(self):
        return self.manual_name or str(self.ingredient or self.product)
