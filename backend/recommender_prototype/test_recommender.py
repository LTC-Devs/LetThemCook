import unittest


from .recommender import (
    PantryItem,
    Recipe,
    UserHistory,
    UserPreferences,
    calculate_expiry_score,
    calculate_pantry_score,
    calculate_preference_score,
    recommend_recipes,
    violates_hard_filters,
)


class RecommenderTests(unittest.TestCase):

    def test_allergy_filters_recipe(self):
        recipe = Recipe(
            id=1,
            name="Peanut Curry",
            ingredients={
                "rice",
                "peanut",
            },
            diets={"vegan"},
            allergens={"peanut"},
        )

        preferences = UserPreferences(
            allergies={"peanut"},
        )

        self.assertTrue(
            violates_hard_filters(
                recipe,
                preferences,
            )
        )

    def test_diet_filters_recipe(self):
        recipe = Recipe(
            id=1,
            name="Chicken Rice",
            ingredients={
                "chicken",
                "rice",
            },
            diets=set(),
        )

        preferences = UserPreferences(
            required_diets={"vegetarian"},
        )

        self.assertTrue(
            violates_hard_filters(
                recipe,
                preferences,
            )
        )

    def test_pantry_score(self):
        recipe = Recipe(
            id=1,
            name="Test Recipe",
            ingredients={
                "tomato",
                "pasta",
                "garlic",
                "onion",
            },
        )

        pantry = [
            PantryItem("tomato"),
            PantryItem("pasta"),
            PantryItem("garlic"),
        ]

        score = calculate_pantry_score(
            recipe,
            pantry,
        )

        self.assertEqual(score, 0.75)

    def test_expiring_ingredient_increases_score(self):
        recipe = Recipe(
            id=1,
            name="Tomato Pasta",
            ingredients={
                "tomato",
                "pasta",
            },
        )

        fresh_pantry = [
            PantryItem(
                "tomato",
                days_to_expiry=6,
            )
        ]

        expiring_pantry = [
            PantryItem(
                "tomato",
                days_to_expiry=1,
            )
        ]

        fresh_score = calculate_expiry_score(
            recipe,
            fresh_pantry,
        )

        expiring_score = calculate_expiry_score(
            recipe,
            expiring_pantry,
        )

        self.assertGreater(
            expiring_score,
            fresh_score,
        )

    def test_filtered_recipes_not_recommended(self):
        recipes = [
            Recipe(
                id=1,
                name="Safe Recipe",
                ingredients={"tomato"},
                diets={"vegetarian"},
            ),
            Recipe(
                id=2,
                name="Peanut Recipe",
                ingredients={"peanut"},
                diets={"vegetarian"},
                allergens={"peanut"},
            ),
        ]

        preferences = UserPreferences(
            required_diets={"vegetarian"},
            allergies={"peanut"},
        )

        recommendations = recommend_recipes(
            recipes=recipes,
            pantry=[
                PantryItem("tomato"),
                PantryItem("peanut"),
            ],
            preferences=preferences,
            history=UserHistory(),
        )

        names = {
            recommendation.recipe.name
            for recommendation in recommendations
        }

        self.assertIn(
            "Safe Recipe",
            names,
        )

        self.assertNotIn(
            "Peanut Recipe",
            names,
        )

    def test_recipe_using_available_ingredients_scores_higher(self):
        recipes = [
            Recipe(
                id=1,
                name="Pantry Recipe",
                ingredients={
                    "tomato",
                    "pasta",
                },
            ),
            Recipe(
                id=2,
                name="Missing Ingredients Recipe",
                ingredients={
                    "potato",
                    "spinach",
                },
            ),
        ]

        recommendations = recommend_recipes(
            recipes=recipes,
            pantry=[
                PantryItem(
                    "tomato",
                    days_to_expiry=2,
                ),
                PantryItem(
                    "pasta",
                    days_to_expiry=100,
                ),
            ],
            preferences=UserPreferences(),
            history=UserHistory(),
        )

        self.assertEqual(
            recommendations[0].recipe.name,
            "Pantry Recipe",
        )


    def test_expired_ingredient_is_not_available(self):
        recipe = Recipe(
            id=1,
            name="Milk Soup",
            ingredients={"milk"},
        )

        pantry = [
            PantryItem(
                "milk",
                days_to_expiry=-2,
            )
        ]

        self.assertEqual(
            calculate_pantry_score(recipe, pantry),
            0.0,
        )

        self.assertIsNone(
            calculate_expiry_score(recipe, pantry)
        )

    def test_missing_expiry_date_returns_none(self):
        recipe = Recipe(
            id=1,
            name="Tomato Soup",
            ingredients={"tomato"},
        )

        pantry = [
            PantryItem("tomato")
        ]

        self.assertIsNone(
            calculate_expiry_score(recipe, pantry)
        )

    def test_liked_ingredient_scores_higher(self):
        recipe_a = Recipe(
            id=1,
            name="Tomato Soup",
            ingredients={"tomato"},
        )

        recipe_b = Recipe(
            id=2,
            name="Mushroom Soup",
            ingredients={"mushroom"},
        )

        preferences = UserPreferences(
            liked_ingredients={"tomato"},
        )

        score_a = calculate_preference_score(
            recipe_a,
            preferences,
        )

        score_b = calculate_preference_score(
            recipe_b,
            preferences,
        )

        self.assertGreater(score_a, score_b)

    def test_reshuffle_excludes_previous_recipe(self):
        recipes = [
            Recipe(
                id=1,
                name="Tomato Soup",
                ingredients={"tomato"},
            ),
            Recipe(
                id=2,
                name="Potato Soup",
                ingredients={"potato"},
            ),
        ]

        pantry = [
            PantryItem("tomato")
        ]

        preferences = UserPreferences()
        history = UserHistory()

        first = recommend_recipes(
            recipes=recipes,
            pantry=pantry,
            preferences=preferences,
            history=history,
            limit=1,
        )

        self.assertEqual(
            first[0].recipe.id,
            1,
        )

        second = recommend_recipes(
            recipes=recipes,
            pantry=pantry,
            preferences=preferences,
            history=history,
            limit=1,
            excluded_recipe_ids={
                first[0].recipe.id
            },
        )

        self.assertEqual(
            second[0].recipe.id,
            2,
        )

        self.assertNotEqual(
            first[0].recipe.id,
            second[0].recipe.id,
        )

if __name__ == "__main__":
    unittest.main()