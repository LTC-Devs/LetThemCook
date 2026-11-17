from .recommender import (
    PantryItem,
    Recipe,
    UserHistory,
    UserPreferences,
    recommend_recipes,
)


recipes = [
    Recipe(
        id=1,
        name="Tomato Pasta",
        ingredients={
            "pasta",
            "tomato",
            "onion",
            "garlic",
            "parmesan",
        },
        diets={"vegetarian"},
        allergens={"milk"},
        tags={
            "italian",
            "pasta",
            "quick",
            "tomato",
        },
    ),

    Recipe(
        id=2,
        name="Vegetable Risotto",
        ingredients={
            "rice",
            "onion",
            "mushroom",
            "parmesan",
        },
        diets={"vegetarian"},
        allergens={"milk"},
        tags={
            "italian",
            "rice",
            "vegetables",
        },
    ),

    Recipe(
        id=3,
        name="Peanut Curry",
        ingredients={
            "rice",
            "peanut",
            "coconut milk",
            "carrot",
            "onion",
        },
        diets={
            "vegetarian",
            "vegan",
        },
        allergens={"peanut"},
        tags={
            "asian",
            "curry",
            "spicy",
        },
    ),

    Recipe(
        id=4,
        name="Chicken Rice",
        ingredients={
            "chicken",
            "rice",
            "onion",
            "carrot",
        },
        diets=set(),
        tags={
            "rice",
            "quick",
        },
    ),

    Recipe(
        id=5,
        name="Tomato Soup",
        ingredients={
            "tomato",
            "lentils",
            "onion",
            "carrot",
            "garlic",
        },
        diets={
            "vegetarian",
            "vegan",
        },
        tags={
            "soup",
            "tomato",
            "healthy",
        },
    ),

    Recipe(
        id=6,
        name="Arrabbiata",
        ingredients={
            "pasta",
            "tomato",
            "garlic",
            "chilli",
        },
        diets={
            "vegetarian",
            "vegan",
        },
        tags={
            "italian",
            "pasta",
            "tomato",
            "spicy",
        },
    ),
]


pantry = [
    PantryItem(
        name="pasta",
        days_to_expiry=100,
    ),
    PantryItem(
        name="tomato",
        days_to_expiry=1,
    ),
    PantryItem(
        name="onion",
        days_to_expiry=4,
    ),
    PantryItem(
        name="garlic",
        days_to_expiry=10,
    ),
    PantryItem(
        name="carrot",
        days_to_expiry=2,
    ),
    PantryItem(
        name="rice",
        days_to_expiry=200,
    ),
]


preferences = UserPreferences(
    required_diets={"vegetarian"},
    allergies={"peanut"},
    liked_ingredients={
        "tomato",
        "garlic",
        "chilli",
    },
    disliked_ingredients={
        "mushroom",
    },
)


history = UserHistory(
    liked_recipe_ids={1},
    disliked_recipe_ids={2},
    last_eaten_days={
        1: 2,
        2: 10,
    },
)


recommendations = recommend_recipes(
    recipes=recipes,
    pantry=pantry,
    preferences=preferences,
    history=history,
)


print("\nRECOMMENDATIONS\n")

for position, recommendation in enumerate(
    recommendations,
    start=1,
):
    print(
        f"{position}. "
        f"{recommendation.recipe.name}"
    )

    print(
        f"   score: "
        f"{recommendation.score:.2%}"
    )

    for name, value in recommendation.components.items():
        if value is None:
            formatted = "N/A"
        else:
            formatted = f"{value:.2%}"

        print(
            f"   {name:12}: {formatted}"
        )

    print()