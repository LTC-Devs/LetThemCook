from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    def handle(self, *args, **opts):
        for name in [
                "Mleko chude", 
                "Chleb pszenny", 
                "Jogurt naturalny",
                "Śmietana", 
                "Ser biały",
                "Mleko bez laktozy"
            ]:
            Product.objects.get_or_create(name=name)