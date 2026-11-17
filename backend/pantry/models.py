from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class PantryItem(models.Model):
    """single stock batch, multiple batches may have different expiry dates"""

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        CONSUMED = "consumed", "Consumed"
        DISCARDED = "discarded", "Discarded"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pantry_items")
    ingredient = models.ForeignKey(
        "recipes.Ingredient", null=True, blank=True, on_delete=models.PROTECT, related_name="pantry_items"
    )
    product = models.ForeignKey(
        "products.Product", null=True, blank=True, on_delete=models.SET_NULL, related_name="pantry_items"
    )
    manual_name = models.CharField(max_length=250, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("1"))
    unit = models.CharField(max_length=40, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    purchased_at = models.DateField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AVAILABLE, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "status", "expiry_date"], name="pantry_expiry_lookup_idx")]
        constraints = [models.CheckConstraint(condition=Q(quantity__gte=0), name="pantry_quantity_nonneg")]

    def clean(self):
        super().clean()
        if not (self.ingredient_id or self.product_id or self.manual_name.strip()):
            raise ValidationError({"manual_name": "Provide an ingredient, product, or manual name."})

    def __str__(self):
        label = self.manual_name or str(self.ingredient or self.product)
        return f"{label}: {self.quantity} {self.unit}".strip()
