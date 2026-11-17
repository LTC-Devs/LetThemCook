from django.db import models

# TODO: not managed copy from origin db
class Product(models.Model):
    name = models.CharField(max_length=300, db_index=True)
    ean = models.CharField(max_length=14, blank=True, db_index=True)
    ingredient = models.ForeignKey(
        "recipes.Ingredient", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="products",
    )


    def __str__(self):
        return self.name
