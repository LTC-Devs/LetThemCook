from decimal import Decimal

from django.test import TestCase, override_settings

from pantry.models import PantryItem
from recipes.models import BaseUnit, Ingredient, Recipe, RecipeItem


@override_settings(LTC_DEMO_MODE=True)
class ShoppingDemoApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ingredient = Ingredient.objects.create(
            canonical_name='Mąka testowa', base_unit=BaseUnit.GRAM,
        )
        cls.recipe = Recipe.objects.create(name='Naleśniki demo', base_servings=2)
        RecipeItem.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient, amount=Decimal('250'),
        )

    def test_plan_and_purchase_without_login(self):
        self.assertEqual(self.client.get('/api/shopping/').json(), [])
        plan = self.client.post(
            '/api/shopping/plan/',
            {'recipe_id': self.recipe.pk, 'servings': 4},
        )
        self.assertEqual(plan.status_code, 201)
        lines = self.client.get('/api/shopping/').json()
        self.assertEqual(len(lines), 1)
        self.assertEqual(Decimal(lines[0]['to_buy']), Decimal('500'))
        result = self.client.post(
            '/api/shopping/purchase/',
            {'ingredient_ids': [self.ingredient.pk]},
            content_type='application/json',
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(PantryItem.objects.count(), 1)
        self.assertEqual(self.client.get('/api/shopping/').json(), [])

    def test_purchase_rejects_unknown_ingredient(self):
        response = self.client.post(
            '/api/shopping/purchase/', {'ingredient_ids': [999999]},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


@override_settings(LTC_DEMO_MODE=False)
class ShoppingDemoDisabledTests(TestCase):
    def test_demo_is_disabled_by_default(self):
        self.assertEqual(self.client.get('/api/shopping/').status_code, 403)
