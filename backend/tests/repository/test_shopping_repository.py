from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.test import TestCase

from pantry.models import PantryItem
from products.models import Product
from recipes.models import BaseUnit, Ingredient, Recipe, RecipeItem
from recommendations.models import PlannedMeal
from shopping.repository import ShoppingLine, build_shopping_list

User = get_user_model()


class ShoppingRepositoryTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="shopper",
            password="testpassword123",
        )

        # Składniki
        self.flour = Ingredient.objects.create(
            canonical_name="Mąka pszenna",
            base_unit=BaseUnit.GRAM,
        )
        self.sugar = Ingredient.objects.create(
            canonical_name="Cukier",
            base_unit=BaseUnit.GRAM,
        )
        self.milk = Ingredient.objects.create(
            canonical_name="Mleko",
            base_unit=BaseUnit.MILLILITER,
        )
        self.salt = Ingredient.objects.create(
            canonical_name="Sól",
            base_unit=BaseUnit.GRAM,
        )
        self.vanilla = Ingredient.objects.create(
            canonical_name="Cukier waniliowy",
            base_unit=BaseUnit.GRAM,
        )

        # Shop products for pantry
        self.flour_product = Product.objects.create(
            ingredient=self.flour,
            full_name="Mąka Szymanowska 1kg",
            package_amount="1kg",
            normalised_amount=1000.0,
        )
        self.sugar_product = Product.objects.create(
            ingredient=self.sugar,
            full_name="Cukier Królewski 1kg",
            package_amount="1kg",
            normalised_amount=1000.0,
        )

        # Recipe: Naleśniki (recipe servings: 2)
        self.recipe = Recipe.objects.create(
            name="Naleśniki",
            base_servings=2,
        )
        # 1. Flour: 250g (required)
        RecipeItem.objects.create(
            recipe=self.recipe,
            ingredient=self.flour,
            amount=Decimal("250.0"),
            is_optional=False,
        )
        # 2. Sugar: 50g (required)
        RecipeItem.objects.create(
            recipe=self.recipe,
            ingredient=self.sugar,
            amount=Decimal("50.0"),
            is_optional=False,
        )
        # 3. Milk: 200ml (required)
        RecipeItem.objects.create(
            recipe=self.recipe,
            ingredient=self.milk,
            amount=Decimal("200.0"),
            is_optional=False,
        )
        # 4. Salt: no quantity ("do smaku") -> omitted
        RecipeItem.objects.create(
            recipe=self.recipe,
            ingredient=self.salt,
            amount=None,
            is_optional=False,
        )
        # 5. Vanilla sugar: optional -> should be omitted
        RecipeItem.objects.create(
            recipe=self.recipe,
            ingredient=self.vanilla,
            amount=Decimal("10.0"),
            is_optional=True,
        )

    def test_unauthenticated_user(self):
        anon = AnonymousUser()
        result = build_shopping_list(anon)
        self.assertIsInstance(result, ValidationError)

    def test_empty_when_no_planned_meals(self):
        lines = build_shopping_list(self.user)
        self.assertEqual(lines, [])

    def test_ignores_non_planned_meals(self):
        # PROPOSED meal not taken into account
        PlannedMeal.objects.create(
            user=self.user,
            recipe=self.recipe,
            servings=2,
            planned_for=date.today(),
            status=PlannedMeal.Status.PROPOSED,
        )
        lines = build_shopping_list(self.user)
        self.assertEqual(lines, [])

    def test_build_shopping_list_with_stock_calculation(self):
        # Planned meal for 4 servings (recipe 2 servings -> factor = 2)
        # Needs:
        # - Flour: 250g * 2 = 500g
        # - Sugar: 50g * 2 = 100g
        # - Milk: 200ml * 2 = 400ml
        PlannedMeal.objects.create(
            user=self.user,
            recipe=self.recipe,
            servings=4,
            planned_for=date.today(),
            status=PlannedMeal.Status.PLANNED,
        )

        # User pantry:
        # - Flour: 200g (missing 300g)
        PantryItem.objects.create(
            user=self.user,
            product=self.flour_product,
            amount=Decimal("200.0"),
            status=PantryItem.Status.AVAILABLE,
        )
        # - Sugar: 150g (needed 100g, enough)
        PantryItem.objects.create(
            user=self.user,
            product=self.sugar_product,
            amount=Decimal("150.0"),
            status=PantryItem.Status.AVAILABLE,
        )
        # - Milk: 0 in stock (missing 400ml)

        lines = build_shopping_list(self.user)

        # milk and flour only in the shopping list
        self.assertEqual(len(lines), 2)

        lines_by_ing_id = {line.ingredient.id: line for line in lines}

        # verify flour
        self.assertIn(self.flour.id, lines_by_ing_id)
        flour_line = lines_by_ing_id[self.flour.id]
        self.assertEqual(flour_line.unit, "g")
        self.assertEqual(flour_line.needed, Decimal("500.0"))
        self.assertEqual(flour_line.in_stock, Decimal("200.0"))
        self.assertEqual(flour_line.to_buy, Decimal("300.0"))

        # verify milk
        self.assertIn(self.milk.id, lines_by_ing_id)
        milk_line = lines_by_ing_id[self.milk.id]
        self.assertEqual(milk_line.unit, "ml")
        self.assertEqual(milk_line.needed, Decimal("400.0"))
        self.assertEqual(milk_line.in_stock, Decimal("0"))
        self.assertEqual(milk_line.to_buy, Decimal("400.0"))

        # Sugar should not appear, there is enough stocked
        self.assertNotIn(self.sugar.id, lines_by_ing_id)

