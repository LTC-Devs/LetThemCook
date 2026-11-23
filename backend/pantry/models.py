import pghistory
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

@pghistory.track(fields=["status"])
class PantryItem(models.Model):
    """single stock batch, multiple batches may have different expiry dates"""

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        CONSUMED = "consumed", "Consumed"
        DISCARDED = "discarded", "Discarded"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pantry_items")
    # product mandatory as link to ingredient
    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name="pantry_items"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=4, help_text="expressed in product.ingredient.base_unit")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AVAILABLE, db_index=True)
    added_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "status", "expires_at"], name="pantry_expiry_lookup_idx")]
        constraints = [models.CheckConstraint(condition=Q(amount__gte=0), name="pantry_amount_nonneg")]

    def __str__(self):
        return f"{self.product.full_name}: {self.amount} {self.product.ingredient.base_unit}"