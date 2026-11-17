from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from products.models import Product
from recipes.models import Ingredient
from .models import PantryItem


class PantryTests(TestCase):
    def test_batches_and_expiration_are_independent(self):
        user = get_user_model().objects.create_user(username="chef", password="testpass")
        milk = Ingredient.objects.create(name="milk")
        today = timezone.localdate()
        first = PantryItem.objects.create(user=user, ingredient=milk, quantity=Decimal("1.5"),
                                          unit="l", expiry_date=today + timedelta(days=1))
        second = PantryItem.objects.create(user=user, ingredient=milk, quantity=Decimal("1.0"),
                                           unit="l", expiry_date=today + timedelta(days=5))
        self.assertNotEqual(first.pk, second.pk)
        self.assertEqual(user.pantry_items.count(), 2)

    def test_stock_can_refer_to_barcode_product(self):
        user = get_user_model().objects.create_user(username="user", password="testpass")
        ingredient = Ingredient.objects.create(name="yogurt")
        product = Product.objects.create(name="Yogurt natural", ean="12345678", ingredient=ingredient)
        entry = PantryItem(user=user, product=product, quantity=Decimal("2"), unit="szt.")
        entry.full_clean()
        entry.save()
        self.assertEqual(entry.product.ingredient, ingredient)
        with self.assertRaises(ValidationError):
            PantryItem(user=user, quantity=Decimal("1")).full_clean()
