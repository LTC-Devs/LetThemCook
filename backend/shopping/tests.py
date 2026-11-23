from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from recipes.models import Ingredient, Recipe, RecipeItem
from .repository import ShoppingList, ShoppingListItem


class ShoppingTests(TestCase):
    def test_list_items_can_link_back_to_recipe(self):
        user = get_user_model().objects.create_user(username="buyer", password="testpass")
        tomato = Ingredient.objects.create(name="tomato")
        recipe = Recipe.objects.create(title="Tomato soup")
        source = RecipeItem.objects.create(recipe=recipe, raw_text="2 pomidory", ingredient=tomato)
        shopping = ShoppingList.objects.create(user=user, title="Dinners")
        item = ShoppingListItem.objects.create(shopping_list=shopping, ingredient=tomato,
                                              source_recipe_item=source, quantity=Decimal("2"),
                                              unit="szt.")
        self.assertEqual(shopping.items.get(), item)
        item.is_checked = True
        item.save(update_fields=["is_checked"])
        self.assertTrue(ShoppingListItem.objects.get(pk=item.pk).is_checked)
        with self.assertRaises(ValidationError):
            ShoppingListItem(shopping_list=shopping).full_clean()
