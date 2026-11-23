from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from pantry.models import PantryItem
from products.models import Product
from recipes.models import BaseUnit, Ingredient

User = get_user_model()


class PantryAndProductTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cook_user",
            password="testpassword123",
        )

    def test_create_and_retrieve_product_and_pantry_item(self):
        # base ingredient
        milk_ingredient = Ingredient.objects.create(
            canonical_name="Mleko",
            base_unit=BaseUnit.MILLILITER,
        )

        # shop product
        milk_product = Product.objects.create(
            ingredient=milk_ingredient,
            ean="5900820001234",
            full_name="Mleko Mlekovita 3.2% 1L",
            package_amount="1L",
            normalised_amount=1000.0,
        )

        # adding pantryitem
        expiry = timezone.now() + timedelta(days=7)
        item = PantryItem.objects.create(
            user=self.user,
            product=milk_product,
            amount=Decimal("1000.0"),
            status=PantryItem.Status.AVAILABLE,
            expires_at=expiry,
        )

        # retrieving from pantry
        retrieved_item = PantryItem.objects.get(id=item.id)
        self.assertEqual(retrieved_item.user, self.user)
        self.assertEqual(retrieved_item.amount, Decimal("1000.0"))
        self.assertEqual(retrieved_item.status, PantryItem.Status.AVAILABLE)
        self.assertEqual(retrieved_item.expires_at, expiry)

        # reference verification
        self.assertEqual(retrieved_item.product.full_name, "Mleko Mlekovita 3.2% 1L")
        self.assertEqual(retrieved_item.product.ean, "5900820001234")
        self.assertEqual(retrieved_item.product.normalised_amount, 1000.0)
        self.assertEqual(retrieved_item.product.ingredient.canonical_name, "Mleko")
        self.assertEqual(retrieved_item.product.ingredient.base_unit, "ml")

        # user and product verification
        self.assertIn(retrieved_item, self.user.pantry_items.all())
        self.assertIn(retrieved_item, milk_product.pantry_items.all())

    def test_generic_product_uniqueness_and_editing(self):
        ingredient = Ingredient.objects.create(
            canonical_name="Cukier",
            base_unit=BaseUnit.GRAM,
        )

        # adding generic product (not tied to specific storebought item details)
        generic_product = Product.objects.create(
            ingredient=ingredient,
            ean="",
            full_name="Cukier",
            package_amount="1kg",
            normalised_amount=1000.0,
        )
        self.assertEqual(Product.objects.filter(ingredient=ingredient, ean="").count(), 1)

        # adding another generic product should violate constraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    ingredient=ingredient,
                    ean="",
                    full_name="Inny Cukier (ogólny)",
                    package_amount="500g",
                    normalised_amount=500.0,
                )

        # editing the generic product
        generic_product.full_name = "Cukier biały (ogólny)"
        generic_product.package_amount = "500g"
        generic_product.normalised_amount = 500.0
        generic_product.save()

        # adding product with details
        branded_product = Product.objects.create(
            ingredient=ingredient,
            ean="5901234567890",
            full_name="Cukier Królewski 1kg",
            package_amount="1kg",
            normalised_amount=1000.0,
        )
        self.assertEqual(Product.objects.filter(ingredient=ingredient).count(), 2)
        self.assertEqual(branded_product.ingredient, ingredient)
