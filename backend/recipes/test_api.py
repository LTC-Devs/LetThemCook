from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import BaseUnit, Ingredient, Recipe, RecipeItem


class RecipeApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        water = Ingredient.objects.create(canonical_name="woda", base_unit=BaseUnit.MILLILITER)
        cls.public = Recipe.objects.create(
            name="Zupa testowa", steps=["Wymieszać składniki."],
        )
        RecipeItem.objects.create(recipe=cls.public, ingredient=water, amount=250, quantity_note="1 szklanka")
        user = get_user_model().objects.create_user(username="private_cook", password="password")
        cls.private = Recipe.objects.create(name="Mój prywatny przepis", owner=user)

    def test_public_recipe_list(self):
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["name"], "Zupa testowa")

    def test_search(self):
        # 'zupa' should not match the substring in 'szczupak'.
        Recipe.objects.create(name="Szczupak w galarecie")
        self.assertEqual(self.client.get("/api/recipes/?q=zupa").json()["count"], 1)
        self.assertEqual(self.client.get("/api/recipes/?q=szczup").json()["count"], 1)
        self.assertEqual(self.client.get("/api/recipes/?q=xyz").json()["count"], 0)

    def test_search_by_ingredient(self):
        self.assertEqual(self.client.get("/api/recipes/?q=woda").json()["count"], 1)
        self.assertEqual(self.client.get("/api/recipes/?q=oda").json()["count"], 0)

    def test_home_suggestions_are_from_public_cookbook(self):
        response = self.client.get("/api/recipes/suggestions/?count=3")
        self.assertEqual(response.status_code, 200)
        recipes = response.json()["results"]
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0]["id"], self.public.pk)
        self.assertEqual(recipes[0]["ingredients"], ["woda"])

    def test_home_suggestions_can_exclude_visible_recipes(self):
        response = self.client.get(
            f"/api/recipes/suggestions/?exclude={self.public.pk}&count=3"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])

    def test_public_detail(self):
        response = self.client.get(f"/api/recipes/{self.public.pk}/")
        self.assertEqual(response.status_code, 200)
        item = response.json()["items"][0]
        self.assertEqual((item["ingredient"], item["unit"], item["quantity_note"]), ("woda", "ml", "1 szklanka"))
        self.assertEqual(response.json()["steps"], ["Wymieszać składniki."])

    def test_private_recipe_not_exposed(self):
        response = self.client.get(f"/api/recipes/{self.private.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_read_only(self):
        self.assertEqual(self.client.post("/api/recipes/").status_code, 405)
