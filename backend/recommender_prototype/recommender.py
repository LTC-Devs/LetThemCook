from __future__ import annotations

from dataclasses import dataclass, field


WEIGHTS = {
    "pantry": 0.40,
    "expiry": 0.25,
    "preference": 0.20,
    "history": 0.10,
    "diversity": 0.05,
}


@dataclass
class Recipe:
    id: int
    name: str
    ingredients: set[str]

    # vegetarian, itp...
    diets: set[str] = field(default_factory=set)

    # peanut, itp...
    allergens: set[str] = field(default_factory=set)

    # dinner, itp...
    tags: set[str] = field(default_factory=set)


@dataclass
class PantryItem:
    name: str

    # expity date
    days_to_expiry: int | None = None

# preferences
@dataclass
class UserPreferences:
    required_diets: set[str] = field(default_factory=set)
    allergies: set[str] = field(default_factory=set)

    liked_ingredients: set[str] = field(default_factory=set)
    disliked_ingredients: set[str] = field(default_factory=set)

    # optional
    excluded_ingredients: set[str] = field(default_factory=set)


@dataclass
class UserHistory:
    liked_recipe_ids: set[int] = field(default_factory=set)
    disliked_recipe_ids: set[int] = field(default_factory=set)

    # recipe_id, ile dni temu jadł przepis
    last_eaten_days: dict[int, int] = field(default_factory=dict)


@dataclass
class Recommendation:
    recipe: Recipe
    score: float
    components: dict[str, float | None]


def normalize(value: str) -> str:
    return value.strip().lower()


def normalize_set(values: set[str]) -> set[str]:
    return {normalize(value) for value in values}


def violates_hard_filters(
    recipe: Recipe,
    preferences: UserPreferences,
) -> bool:
    recipe_ingredients = normalize_set(recipe.ingredients)
    recipe_allergens = normalize_set(recipe.allergens)
    recipe_diets = normalize_set(recipe.diets)

    user_allergies = normalize_set(preferences.allergies)
    required_diets = normalize_set(preferences.required_diets)
    excluded = normalize_set(preferences.excluded_ingredients)

    # alergia - nope
    if recipe_allergens & user_allergies:
        return True

    # jeżeli alergen występuje też jako zwykły składnik
    if recipe_ingredients & user_allergies:
        return True

    # user bardzo nie chce - nope
    if recipe_ingredients & excluded:
        return True

    # np. vegans
    if not required_diets.issubset(recipe_diets):
        return True

    return False


def calculate_pantry_score(
    recipe: Recipe,
    pantry: list[PantryItem],
) -> float:
    ingredients = normalize_set(recipe.ingredients)

    if not ingredients:
        return 0.0

    pantry_names = {
    normalize(item.name)
    for item in pantry
    if (
        item.days_to_expiry is None
        or item.days_to_expiry >= 0
    )
    }

    available = ingredients & pantry_names

    return len(available) / len(ingredients)


def calculate_expiry_score(
    recipe: Recipe,
    pantry: list[PantryItem],
    expiry_window_days: int = 7,
) -> float | None:
    if expiry_window_days <= 0:
        raise ValueError("Expiry window must be positive")

    ingredients = normalize_set(recipe.ingredients)
    urgencies_by_ingredient = {}

    for item in pantry:
        name = normalize(item.name)

        if name not in ingredients:
            continue

        if item.days_to_expiry is None:
            continue

        if item.days_to_expiry < 0:
            continue

        urgency = max(
            0.0,
            1.0 - item.days_to_expiry / expiry_window_days
        )

        urgencies_by_ingredient[name] = max(
            urgencies_by_ingredient.get(name, 0.0),
            urgency
        )

    if not urgencies_by_ingredient:
        return None

    return (
        sum(urgencies_by_ingredient.values())
        / len(urgencies_by_ingredient)
    )



def calculate_preference_score(
    recipe: Recipe,
    preferences: UserPreferences,
) -> float | None:
    liked = normalize_set(preferences.liked_ingredients)
    disliked = normalize_set(preferences.disliked_ingredients)

    # no preferences
    if not liked and not disliked:
        return None

    ingredients = normalize_set(recipe.ingredients)

    liked_matches = len(ingredients & liked)
    disliked_matches = len(ingredients & disliked)

    liked_ratio = (
        liked_matches / len(ingredients)
        if ingredients
        else 0
    )

    disliked_ratio = (
        disliked_matches / len(ingredients)
        if ingredients
        else 0
    )

    # 0.5 = neutralnie
    score = (
        0.5
        + 0.5 * liked_ratio
        - 0.75 * disliked_ratio
    )

    return max(0.0, min(score, 1.0))


def jaccard_similarity(
    first: set[str],
    second: set[str],
) -> float:
    first = normalize_set(first)
    second = normalize_set(second)

    union = first | second

    if not union:
        return 0.0

    intersection = first & second

    return len(intersection) / len(union)


def recipe_similarity(
    first: Recipe,
    second: Recipe,
) -> float:
    first_features = first.ingredients | first.tags
    second_features = second.ingredients | second.tags

    return jaccard_similarity(
        first_features,
        second_features,
    )


def calculate_history_score(
    recipe: Recipe,
    all_recipes: list[Recipe],
    history: UserHistory,
) -> float | None:
    if (
        not history.liked_recipe_ids
        and not history.disliked_recipe_ids
    ):
        return None

    recipe_by_id = {
        item.id: item
        for item in all_recipes
    }

    liked_similarities = []
    disliked_similarities = []

    for recipe_id in history.liked_recipe_ids:
        liked_recipe = recipe_by_id.get(recipe_id)

        if liked_recipe is not None:
            liked_similarities.append(
                recipe_similarity(recipe, liked_recipe)
            )

    for recipe_id in history.disliked_recipe_ids:
        disliked_recipe = recipe_by_id.get(recipe_id)

        if disliked_recipe is not None:
            disliked_similarities.append(
                recipe_similarity(recipe, disliked_recipe)
            )

    best_liked_similarity = max(
        liked_similarities,
        default=0.0,
    )

    best_disliked_similarity = max(
        disliked_similarities,
        default=0.0,
    )

    score = (
        0.5
        + 0.5 * best_liked_similarity
        - 0.75 * best_disliked_similarity
    )

    return max(0.0, min(score, 1.0))


def calculate_diversity_score(
    recipe: Recipe,
    history: UserHistory,
    full_score_after_days: int = 30,
) -> float | None:
    # no history 
    if not history.last_eaten_days:
        return None

    days_since_last_eaten = history.last_eaten_days.get(
        recipe.id
    )

    # nie jedzony dostaje maks premie
    if days_since_last_eaten is None:
        return 1.0

    return min(
        max(days_since_last_eaten, 0)
        / full_score_after_days,
        1.0,
    )


def calculate_final_score(
    components: dict[str, float | None],
) -> float:
    weighted_score = 0.0
    active_weights = 0.0

    for component_name, component_value in components.items():
        if component_value is None:
            continue

        weight = WEIGHTS[component_name]

        weighted_score += component_value * weight
        active_weights += weight

    if active_weights == 0:
        return 0.0

    # score wyłącznie z dostępnych danych
    return weighted_score / active_weights



def recommend_recipes(
    recipes: list[Recipe],
    pantry: list[PantryItem],
    preferences: UserPreferences,
    history: UserHistory,
    limit: int = 5,
    excluded_recipe_ids: set[int] | None = None,
) -> list[Recommendation]:
    recommendations = []
    excluded_recipe_ids = excluded_recipe_ids or set()

    for recipe in recipes:
        # reshuffle
        if recipe.id in excluded_recipe_ids:
            continue

        # alergie, diety, wykluczone składniki
        if violates_hard_filters(
            recipe,
            preferences,
        ):
            continue

        components = {
            "pantry": calculate_pantry_score(
                recipe,
                pantry,
            ),
            "expiry": calculate_expiry_score(
                recipe,
                pantry,
            ),
            "preference": calculate_preference_score(
                recipe,
                preferences,
            ),
            "history": calculate_history_score(
                recipe,
                recipes,
                history,
            ),
            "diversity": calculate_diversity_score(
                recipe,
                history,
            ),
        }

        score = calculate_final_score(components)

        recommendations.append(
            Recommendation(
                recipe=recipe,
                score=score,
                components=components,
            )
        )

    recommendations.sort(
        key=lambda recommendation: recommendation.score,
        reverse=True,
    )

    return recommendations[:limit]