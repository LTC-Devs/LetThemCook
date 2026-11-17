from django.contrib.auth import get_user_model
from django.test import TestCase

from recipes.models import Allergen, Diet, Ingredient
from .models import UserPreferences


class UserPreferencesTests(TestCase):
    def test_user_preferences_and_relationships(self):
        user = get_user_model().objects.create_user(username="someone", password="testpass")
        pref = UserPreferences.objects.create(user=user, household_size=3)
        allergy = Allergen.objects.create(name="soy")
        diet = Diet.objects.create(name="vegan")
        ingredient = Ingredient.objects.create(name="tomato")
        pref.allergies.add(allergy)
        pref.required_diets.add(diet)
        pref.liked_ingredients.add(ingredient)
        self.assertEqual(user.food_preferences.household_size, 3)
        self.assertEqual(list(pref.allergies.all()), [allergy])
        self.assertEqual(list(pref.required_diets.all()), [diet])
        self.assertEqual(list(pref.liked_ingredients.all()), [ingredient])
