from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from pantry.models import PantryItem
from recipes.models import Allergen, Diet, Ingredient, Recipe, RecipeItem
from users.models import UserPreferences
from .models import CookingHistory, MealPlan, PlannedMeal, RecipeFeedback
from .orm_bridge import recommend_from_database


class RecommendationsORMTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="chef", password="testpass")
        self.pref = UserPreferences.objects.create(user=self.user)

    def _recipe(self, title, ingredient, status=Recipe.ParsingStatus.VERIFIED):
        recipe = Recipe.objects.create(title=title, parsing_status=status)
        RecipeItem.objects.create(recipe=recipe, position=1, ingredient=ingredient)
        return recipe

    def test_bridge_recommends_only_verified_safe_recipes(self):
        tomato = Ingredient.objects.create(name="tomato")
        peanut = Ingredient.objects.create(name="peanuts")
        allergy = Allergen.objects.create(name="peanuts")
        peanut.allergens.add(allergy)
        self.pref.allergies.add(allergy)
        vegan = Diet.objects.create(name="vegan")
        self.pref.required_diets.add(vegan)

        safe = self._recipe("Tomato soup", tomato)
        safe.diets.add(vegan)
        unsafe = self._recipe("Nut paste", peanut)
        unsafe.diets.add(vegan)
        raw = self._recipe("Unreviewed tomato", tomato, Recipe.ParsingStatus.RAW)
        raw.diets.add(vegan)
        incomplete = Recipe.objects.create(title="Unlinked OCR", parsing_status=Recipe.ParsingStatus.VERIFIED)
        RecipeItem.objects.create(recipe=incomplete, raw_text="garlic or onions")
        incomplete.diets.add(vegan)
        PantryItem.objects.create(user=self.user, ingredient=tomato, quantity=Decimal("1"),
                                  expiry_date=timezone.localdate() + timedelta(days=1))

        results = recommend_from_database(self.user)
        self.assertEqual([item.recipe.id for item in results], [safe.id])
        self.assertNotIn(unsafe.id, [r.recipe.id for r in results])
        self.assertNotIn(raw.id, [r.recipe.id for r in results])
        self.assertNotIn(incomplete.id, [r.recipe.id for r in results])

    def test_feedback_cooking_history_and_mealplan(self):
        tomato = Ingredient.objects.create(name="tomato")
        recipe = self._recipe("Tomato soup", tomato)
        RecipeFeedback.objects.create(user=self.user, recipe=recipe, value=RecipeFeedback.Value.LIKE)
        CookingHistory.objects.create(user=self.user, recipe=recipe, cooked_at=timezone.now())
        today = timezone.localdate()
        plan = MealPlan.objects.create(user=self.user, start_date=today, end_date=today+timedelta(days=7))
        planned = PlannedMeal.objects.create(plan=plan, recipe=recipe, planned_for=today, servings=2)
        self.assertEqual(self.user.recipe_feedback.count(), 1)
        self.assertEqual(self.user.cooking_history.count(), 1)
        self.assertEqual(plan.meals.get().pk, planned.pk)
        self.assertEqual([r.recipe.id for r in recommend_from_database(self.user)], [recipe.id])
        self.assertEqual(recommend_from_database(self.user, excluded_recipe_ids={recipe.id}), [])
