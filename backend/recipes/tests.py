from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import (Allergen, Category, Cookbook, Diet, DietCategory,
                     Ingredient, Recipe, RecipeItem, Substitution)


class CookbookORMTests(TestCase):
    def setUp(self):
        self.book = Cookbook.objects.get(title="Kuchnia Polska", edition_year=1985)
        self.section = Category.objects.create(name="PRZEKĄSKI ZIMNE I GORĄCE")
        self.subsection = Category.objects.create(name="Kanapki", parent=self.section)

    def test_same_source_number_is_allowed(self):
        # OCR currently contains repeated recipe numbers, including across categories.
        first = Recipe.objects.create(title="Kanapki z szynką", cookbook=self.book,
                                      category=self.subsection, source_number=1)
        second = Recipe.objects.create(title="Inna pozycja", cookbook=self.book,
                                       category=self.subsection, source_number=1)
        self.assertNotEqual(first.pk, second.pk)
        self.assertEqual(self.book.recipes.count(), 2)
        self.assertEqual(list(self.section.children.all()), [self.subsection])

    def test_unreviewed_recipe_preserves_original_line(self):
        recipe = Recipe.objects.create(title="Z książki", cookbook=self.book,
                                       raw_ingredients=["2—3 łyżki masła lub margaryny"],
                                       review_notes=["check amounts"])
        item = RecipeItem.objects.create(recipe=recipe, position=1,
                                         raw_text="2—3 łyżki masła lub margaryny")
        self.assertEqual(recipe.parsing_status, Recipe.ParsingStatus.RAW)
        self.assertIsNone(item.ingredient)
        self.assertEqual(recipe.raw_ingredients[0], item.raw_text)

    def test_quantities_and_subrecipes(self):
        butter = Ingredient.objects.create(name="masło")
        egg = Ingredient.objects.create(name="jajko")
        base = Recipe.objects.create(title="Pasta jajeczna")
        recipe = Recipe.objects.create(title="Kanapki")
        item = RecipeItem(recipe=recipe, position=1, ingredient=butter,
                          amount=Decimal("2.0"), amount_max=Decimal("3.0"), unit="łyżka")
        item.full_clean()
        item.save()
        self.assertEqual(item.amount_max, Decimal("3.0"))
        nested = RecipeItem(recipe=recipe, position=2, sub_recipe=base, raw_text="pasta")
        nested.full_clean()
        nested.save()
        self.assertEqual(recipe.items.count(), 2)
        with self.assertRaises(ValidationError):
            RecipeItem(recipe=recipe, ingredient=egg, sub_recipe=base).full_clean()
        with self.assertRaises(ValidationError):
            RecipeItem(recipe=recipe, raw_text="range", amount=5, amount_max=2).full_clean()

    def test_diet_allergen_and_substitution(self):
        peanuts = Allergen.objects.create(name="peanuts")
        animal = DietCategory.objects.create(name="animal-based")
        vegan = Diet.objects.create(name="vegan")
        vegan.excluded_categories.add(animal)
        milk = Ingredient.objects.create(name="milk")
        milk.diet_categories.add(animal)
        nut = Ingredient.objects.create(name="peanut butter")
        nut.allergens.add(peanuts)
        substitute = Substitution.objects.create(ingredient=milk, substitute=nut, ratio=Decimal("1.5000"))
        self.assertEqual(substitute.ratio, Decimal("1.5000"))
        self.assertEqual(nut.allergens.first(), peanuts)
        self.assertIn(animal, vegan.excluded_categories.all())
        with self.assertRaises(ValidationError):
            Substitution(ingredient=milk, substitute=milk).full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Substitution.objects.create(ingredient=milk, substitute=nut)

    def test_custom_recipe_is_owned_by_user(self):
        user = get_user_model().objects.create_user(username="testchef", password="testpass")
        recipe = Recipe.objects.create(title="My smoothie", owner=user)
        self.assertEqual(list(user.custom_recipes.all()), [recipe])
