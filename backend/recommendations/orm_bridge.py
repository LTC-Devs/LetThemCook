"""Read-only adapter from Django ORM records to the existing pure-Python scorer.

Only verified, fully normalized simple recipes are eligible. Raw OCR and recipes
with unresolved component recipes are intentionally excluded rather than guessed.
"""
from django.db.models import Q
from django.utils import timezone

from pantry.models import PantryItem as DBPantryItem
from recipes.models import Recipe
from users.models import UserPreferences as DBUserPreferences
from recommender_prototype.recommender import (
    PantryItem, Recipe as ScoringRecipe, UserHistory, UserPreferences,
    recommend_recipes,
)

from .models import CookingHistory, RecipeFeedback


def recommend_from_database(user, limit=5, excluded_recipe_ids=None):
    """Return scorer Recommendation dataclasses for an authenticated user.

    `Recommendation.recipe.id` is the database Recipe PK. Caller decides how to
    serialize the recommendations; no new API endpoint is added here.
    """
    if not user.is_authenticated:
        raise ValueError("An authenticated user is required.")

    pref = DBUserPreferences.objects.filter(user=user).first()
    preferences = UserPreferences(
        required_diets=set(pref.required_diets.values_list("name", flat=True)) if pref else set(),
        allergies=set(pref.allergies.values_list("name", flat=True)) if pref else set(),
        excluded_ingredients=set(pref.excluded_ingredients.values_list("name", flat=True)) if pref else set(),
        liked_ingredients=set(pref.liked_ingredients.values_list("name", flat=True)) if pref else set(),
        disliked_ingredients=set(pref.disliked_ingredients.values_list("name", flat=True)) if pref else set(),
    )

    recipe_rows = (Recipe.objects
        .filter(parsing_status=Recipe.ParsingStatus.VERIFIED)
        .filter(Q(owner__isnull=True) | Q(owner=user))
        .select_related("category")
        .prefetch_related("diets", "items__ingredient__allergens")
    )
    recipes = []
    for row in recipe_rows:
        items = list(row.items.all())
        if not items or any(item.ingredient_id is None or item.sub_recipe_id for item in items):
            continue
        ingredients = {item.ingredient.name for item in items}
        allergens = {
            allergen.name for item in items for allergen in item.ingredient.allergens.all()
        }
        recipes.append(ScoringRecipe(
            id=row.id, name=row.title, ingredients=ingredients,
            diets={diet.name for diet in row.diets.all()}, allergens=allergens,
            tags={row.category.name} if row.category_id else set(),
        ))

    today = timezone.localdate()
    pantry = []
    stock = (DBPantryItem.objects.filter(user=user, status=DBPantryItem.Status.AVAILABLE)
             .select_related("ingredient", "product__ingredient"))
    for item in stock:
        if item.amount <= 0:
            continue
        ingredient = item.ingredient or (item.product.ingredient if item.product_id else None)
        name = ingredient.name if ingredient else item.manual_name.strip()
        if not name:
            continue
        remaining_days = (item.expiry_date - today).days if item.expiry_date else None
        if remaining_days is not None and remaining_days < 0:
            continue
        pantry.append(PantryItem(name=name, days_to_expiry=remaining_days))

    liked_ids = set(RecipeFeedback.objects.filter(user=user, value=RecipeFeedback.Value.LIKE)
                    .values_list("recipe_id", flat=True))
    disliked_ids = set(RecipeFeedback.objects.filter(user=user, value=RecipeFeedback.Value.DISLIKE)
                       .values_list("recipe_id", flat=True))
    last_eaten = {}
    for entry in CookingHistory.objects.filter(user=user).order_by("-cooked_at"):
        if entry.recipe_id not in last_eaten:
            last_eaten[entry.recipe_id] = max(0, (today - timezone.localtime(entry.cooked_at).date()).days)

    return recommend_recipes(
        recipes=recipes,
        pantry=pantry,
        preferences=preferences,
        history=UserHistory(
            liked_recipe_ids=liked_ids,
            disliked_recipe_ids=disliked_ids,
            last_eaten_days=last_eaten,
        ),
        limit=limit,
        excluded_recipe_ids=excluded_recipe_ids,
    )
