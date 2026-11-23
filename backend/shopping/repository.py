from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.utils import timezone

from pantry.models import PantryItem
from recommendations.models import PlannedMeal
from recipes.models import Ingredient, Recipe, RecipeItem

ACTIVE_STATUSES = {PlannedMeal.Status.PLANNED}

@dataclass
class ShoppingLine:
    ingredient: Ingredient
    unit: str
    needed: Decimal
    in_stock: Decimal
    to_buy: Decimal

def build_shopping_list(user) -> list[Decimal]:
    if not user.is_authenticated:
        return ValidationError("User has to be logged in")

    meals = PlannedMeal.objects.filter(
        user=user, status__in=ACTIVE_STATUSES
    )

    needed = defaultdict(Decimal)
    ingredients = {}
    no_quantity = []

    for meal in meals:
        recipe: Recipe = meal.recipe
        factor = Decimal(meal.servings) / Decimal(recipe.base_servings or meal.servings)
        for item in recipe.items.select_related("ingredient").all():
            if item.is_optional:
                continue
            if item.amount is None:
                no_quantity.append(item)
                continue
            qty = item.amount_max or item.amount
            needed[item.ingredient_id] += qty * factor
            ingredients[item.ingredient_id] = item.ingredient

    stock = dict(
        PantryItem.objects.filter(user=user, status=PantryItem.Status.AVAILABLE)
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
            .values("product__ingredient_id")
            .annotate(total=Sum("amount"))
            .values_list("product__ingredient_id", "total")
    )

    lines = []
    for ing_id, need_count in needed.items():
        stock_count = stock.get(ing_id) or Decimal("0")
        if need_count > stock_count:
            ingredient: Ingredient = ingredients[ing_id]
            lines.append(ShoppingLine(
                ingredient, 
                ingredient.base_unit, 
                need_count, 
                stock_count,
                need_count - stock_count
            ))

    return lines