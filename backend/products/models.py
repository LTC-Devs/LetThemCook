from django.db import models
from django.db.models import Q, UniqueConstraint

# TODO: not managed copy from origin db
class Product(models.Model):
    """Represents storebought product or a generic mapping to ingredient"""
    ingredient = models.ForeignKey(
        "recipes.Ingredient",
        on_delete=models.CASCADE,
        related_name="products",
        help_text="Mapping to normalized canonical ingredient",
    )
    ean = models.CharField(max_length=14, blank=True, db_index=True)
    full_name = models.CharField(max_length=300, db_index=True, blank=True, help_text="e.g. Mleko Mlekovita 3.2% 1L")
    package_amount = models.CharField(max_length=50, blank=True, help_text="e.g. 1L, 250g")
    normalised_amount = models.FloatField(help_text="Amount in ingredient.base_unit (e.g. 1000 for 1L if base_unit=ml)")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["ingredient"], 
                condition=Q(ean=""), 
                name="one_generic_product_per_ingredient"
            )
        ]
    
    def __str__(self):
        return self.full_name