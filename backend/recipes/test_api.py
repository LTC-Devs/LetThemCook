from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Recipe, RecipeItem


class RecipeApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.public = Recipe.objects.create(
            title="Zupa testowa", instructions="Wymieszać składniki.",
            raw_ingredients=["1 szklanka wody"],
        )
        RecipeItem.objects.create(recipe=cls.public, raw_text="1 szklanka wody")
        user = get_user_model().objects.create_user(username="private_cook", password="password")
        cls.private = Recipe.objects.create(title="Mój prywatny przepis", owner=user)

    def test_public_recipe_list(self):
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["title"], "Zupa testowa")

    def test_search(self):
        self.assertEqual(self.client.get("/api/recipes/?q=zupa").json()["count"], 1)
        self.assertEqual(self.client.get("/api/recipes/?q=xyz").json()["count"], 0)

    def test_public_detail(self):
        response = self.client.get(f"/api/recipes/{self.public.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["raw_text"], "1 szklanka wody")

    def test_private_recipe_not_exposed(self):
        response = self.client.get(f"/api/recipes/{self.private.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_read_only(self):
        self.assertEqual(self.client.post("/api/recipes/").status_code, 405)
