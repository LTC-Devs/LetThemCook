from decimal import Decimal
from django.test import TestCase

from recipes.models import BaseUnit, Ingredient, Recipe, RecipeItem


class RecipeModelsTestCase(TestCase):
    def test_create_and_retrieve_recipe_with_ingredient(self):
        # ingredient
        flour = Ingredient.objects.create(
            canonical_name="Mąka pszenna",
            base_unit=BaseUnit.GRAM,
        )

        # recipe
        pancakes = Recipe.objects.create(
            name="Naleśniki klasyczne",
            base_servings=4,
            steps=["Wymieszaj składniki i smaż na rozgrzanej patelni."],
        )

        # recipeitem: ingredient <-> recipe
        item = RecipeItem.objects.create(
            recipe=pancakes,
            ingredient=flour,
            amount=Decimal("250.0"),
            quantity_note="przesiana przez sitko",
        )

        retrieved_recipe = Recipe.objects.get(id=pancakes.id)
        self.assertEqual(retrieved_recipe.name, "Naleśniki klasyczne")
        self.assertEqual(retrieved_recipe.base_servings, 4)

        recipe_items = retrieved_recipe.items.all()
        self.assertEqual(recipe_items.count(), 1)

        retrieved_item = recipe_items.first()
        self.assertEqual(retrieved_item.ingredient.canonical_name, "Mąka pszenna")
        self.assertEqual(retrieved_item.ingredient.base_unit, "g")
        self.assertEqual(retrieved_item.amount, Decimal("250.0"))
        self.assertEqual(retrieved_item.quantity_note, "przesiana przez sitko")

