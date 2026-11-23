"""Integration checks for the same pantry stock used by shopping."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from products.models import Product
from recipes.models import BaseUnit, Ingredient, Recipe, RecipeItem
from recommendations.models import PlannedMeal
from .models import PantryItem


@override_settings(LTC_DEMO_MODE=True)
class PantryDemoApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ham = Ingredient.objects.create(canonical_name='szynka', base_unit=BaseUnit.GRAM)
        cls.eggs = Ingredient.objects.create(canonical_name='jajko', base_unit=BaseUnit.PIECE)
        cls.recipe = Recipe.objects.create(name='Kanapka demo', base_servings=1)
        RecipeItem.objects.create(recipe=cls.recipe, ingredient=cls.ham, amount=100)

    def add_item(self, ingredient_id=None, amount='100', expires_on=None):
        return self.client.post('/api/pantry/', {
            'ingredient_id': ingredient_id or self.ham.pk,
            'amount': amount,
            'expires_on': expires_on,
        }, content_type='application/json')

    def test_ingredients_are_from_the_same_catalogue(self):
        response = self.client.get('/api/pantry/ingredients/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([(x['name'], x['unit']) for x in response.json()], [('jajko', 'pcs'), ('szynka', 'g')])

    def test_create_update_and_delete_affect_shopping_list(self):
        plan = self.client.post('/api/shopping/plan/', {'recipe_id': self.recipe.pk, 'servings': 1})
        self.assertEqual(plan.status_code, 201)
        self.assertEqual(Decimal(self.client.get('/api/shopping/').json()[0]['to_buy']), Decimal('100'))

        created = self.add_item(amount='100', expires_on='2030-05-10')
        self.assertEqual(created.status_code, 201, created.content)
        item_id = created.json()['id']
        self.assertEqual(created.json()['unit'], 'g')
        self.assertEqual(created.json()['expires_on'], '2030-05-10')
        self.assertEqual(self.client.get('/api/shopping/').json(), [])
        self.assertEqual(len(self.client.get('/api/pantry/').json()), 1)

        updated = self.client.patch(
            f'/api/pantry/{item_id}/', {'amount': '40', 'expires_on': None},
            content_type='application/json',
        )
        self.assertEqual(updated.status_code, 200, updated.content)
        self.assertIsNone(updated.json()['expires_on'])
        self.assertEqual(Decimal(self.client.get('/api/shopping/').json()[0]['to_buy']), Decimal('60'))

        deleted = self.client.delete(f'/api/pantry/{item_id}/')
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(self.client.get('/api/pantry/').json(), [])
        self.assertEqual(Decimal(self.client.get('/api/shopping/').json()[0]['to_buy']), Decimal('100'))
        entry = PantryItem.objects.get(pk=item_id)
        self.assertEqual(entry.status, PantryItem.Status.DISCARDED)
        self.assertIsNotNone(entry.finished_at)

    def test_multiple_batches_and_expired_stock_are_not_available(self):
        PlannedMeal.objects.create(user=get_user_model().objects.create(username='ltc-demo'),
                                   recipe=self.recipe, servings=1, planned_for=timezone.localdate())
        yesterday = (timezone.localdate() - timedelta(days=2)).isoformat()
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        first = self.add_item(amount='40', expires_on=yesterday)
        second = self.add_item(amount='20', expires_on=tomorrow)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        response = self.client.get('/api/pantry/').json()
        self.assertEqual(len(response), 2)
        self.assertEqual({i['expiry_status'] for i in response}, {'expired', 'soon'})
        # Only the 20 g batch not yet expired counts towards shopping.
        self.assertEqual(Decimal(self.client.get('/api/shopping/').json()[0]['to_buy']), Decimal('80'))

    def test_edit_ingredient_changes_stock_mapping(self):
        created = self.add_item(amount='3')
        item_id = created.json()['id']
        response = self.client.patch(
            f'/api/pantry/{item_id}/', {'ingredient_id': self.eggs.pk, 'amount': '2'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['ingredient_name'], 'jajko')
        self.assertEqual(response.json()['unit'], 'pcs')
        self.assertEqual(PantryItem.objects.get(pk=item_id).product.ingredient_id, self.eggs.pk)

    def test_invalid_inputs_and_unknown_items(self):
        for amount in ['0', '-2', '0.00001']:
            self.assertEqual(self.add_item(amount=amount).status_code, 400)
        self.assertEqual(self.add_item(ingredient_id=999999).status_code, 404)
        self.assertEqual(self.add_item(expires_on='nie-data').status_code, 400)
        self.assertEqual(self.client.patch('/api/pantry/99999/', {'amount': '1'}, content_type='application/json').status_code, 404)
        self.assertEqual(self.client.delete('/api/pantry/99999/').status_code, 404)

    def test_cannot_edit_other_users_stock(self):
        someone_else = get_user_model().objects.create(username='someone-else')
        product = Product.objects.create(ingredient=self.ham, full_name='Szynka', normalised_amount=1.0)
        other_item = PantryItem.objects.create(user=someone_else, product=product, amount=5)
        self.assertEqual(self.client.get('/api/pantry/').json(), [])
        self.assertEqual(self.client.delete(f'/api/pantry/{other_item.pk}/').status_code, 404)
        self.assertEqual(PantryItem.objects.get(pk=other_item.pk).status, PantryItem.Status.AVAILABLE)


@override_settings(LTC_DEMO_MODE=False)
class PantryDemoDisabledTests(TestCase):
    def test_access_requires_explicit_demo_mode(self):
        self.assertEqual(self.client.get('/api/pantry/').status_code, 403)
        self.assertEqual(self.client.get('/api/pantry/ingredients/').status_code, 403)
        self.assertEqual(self.client.post('/api/pantry/', {'ingredient_id': 1, 'amount': '10'}).status_code, 403)
        self.assertEqual(self.client.delete('/api/pantry/1/').status_code, 403)
