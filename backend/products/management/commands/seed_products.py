from django.core.management.base import BaseCommand

from products.models import Product
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **opts):
        for full_name, ingredient, amount in [
            ("Mleko chude", "mleko", 1000),
            ("Chleb pszenny", "chleb", 500),
            ("Jogurt naturalny", "jogurt", 400),
            ("Śmietana", "śmietana", 200),
            ("Ser biały", "twaróg", 250),
        ]:
            ingredient = Ingredient.objects.filter(canonical_name=ingredient).first()
            if ingredient:  # the ingredients come from the cookbook import
                Product.objects.get_or_create(full_name=full_name, defaults={"ingredient": ingredient, "normalised_amount": amount})
