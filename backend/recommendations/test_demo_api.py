"""End-to-end scoring checks against actual Recipe and Pantry tables."""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.utils import timezone

from pantry.models import PantryItem
from products.models import Product
from recipes.models import Ingredient, BaseUnit, Recipe, RecipeItem
from users.demo import demo_user


@override_settings(LTC_DEMO_MODE=True)
class RecommendationDemoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.eggplant = Ingredient.objects.create(canonical_name='bakłażany', base_unit=BaseUnit.GRAM)
        cls.ham = Ingredient.objects.create(canonical_name='szynka', base_unit=BaseUnit.GRAM)
        cls.eggplant_recipe = Recipe.objects.create(name='Bakłażany pieczone')
        RecipeItem.objects.create(recipe=cls.eggplant_recipe, ingredient=cls.eggplant, amount=500)
        cls.ham_recipe = Recipe.objects.create(name='Kanapki', base_servings=1)
        RecipeItem.objects.create(recipe=cls.ham_recipe, ingredient=cls.ham, amount=100)

    def stock(self, ingredient, amount, expires_at=None):
        product = Product.objects.create(
            ingredient=ingredient, ean='', full_name=ingredient.canonical_name, normalised_amount=1,
        )
        return PantryItem.objects.create(
            user=demo_user(), product=product, amount=amount, expires_at=expires_at,
        )

    def test_full_match_outweighs_missing_ingredient(self):
        self.stock(self.eggplant, 500)
        response = self.client.get('/api/recommendations/?count=2')
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']
        self.assertEqual([r['id'] for r in results], [self.eggplant_recipe.pk, self.ham_recipe.pk])
        self.assertEqual(results[0]['score'], 85)
        self.assertEqual(results[1]['score'], 0)
        self.assertEqual(results[0]['score_breakdown'], {
            'availability': 60, 'few_missing': 25, 'expiry': 0,
        })

    def test_expiring_stock_boosts_ranking(self):
        self.stock(self.eggplant, 500, expires_at=timezone.now() + timedelta(hours=12))
        self.stock(self.ham, 100)
        results = self.client.get('/api/recommendations/?count=2').json()['results']
        self.assertEqual(results[0]['id'], self.eggplant_recipe.pk)
        self.assertEqual(results[0]['score'], 100)
        self.assertEqual(results[1]['score'], 85)

    def test_expired_stock_ignored(self):
        self.stock(self.eggplant, 500, expires_at=timezone.now() - timedelta(hours=1))
        results = self.client.get('/api/recommendations/?count=2').json()['results']
        first = next(item for item in results if item['id'] == self.eggplant_recipe.pk)
        self.assertEqual(first['score'], 0)

    def test_exclusions_and_private_recipes(self):
        from django.contrib.auth import get_user_model
        private_user = get_user_model().objects.create_user(username='other-demo')
        Recipe.objects.create(name='Prywatny przepis', owner=private_user)
        response = self.client.get(f'/api/recommendations/?exclude={self.eggplant_recipe.pk}&count=2')
        self.assertEqual([r['id'] for r in response.json()['results']], [self.ham_recipe.pk])


@override_settings(LTC_DEMO_MODE=False)
class RecommendationDisabledTests(TestCase):
    def test_demo_disabled(self):
        self.assertEqual(self.client.get('/api/recommendations/').status_code, 403)
