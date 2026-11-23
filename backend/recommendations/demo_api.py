"""Read-only, explainable recipe recommendations for the local LTC demo."""
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from pantry.models import PantryItem
from recipes.models import Recipe
from users.demo import demo_user
from .scoring import score_recipe


def _quantified_requirements(recipe, available):
    """Use max of a range; optional/unquantified lines do not affect the score.

    For alternative ingredient groups (e.g. margarine OR butter), choose the
    option best covered by pantry stock; don't require both alternatives.
    """
    required = defaultdict(lambda: Decimal(0))
    alternatives = defaultdict(list)
    unquantified = 0
    for item in recipe.items.all():
        if item.is_optional:
            continue
        quantity = item.amount_max if item.amount_max is not None else item.amount
        if quantity is None:
            unquantified += 1
            continue
        if quantity <= 0:
            continue
        if item.alternative_group:
            alternatives[item.alternative_group].append((item.ingredient_id, quantity, item.pk))
        else:
            required[item.ingredient_id] += quantity
    for choices in alternatives.values():
        ingredient_id, quantity, _ = max(
            choices,
            key=lambda row: (
                min(Decimal(1), available.get(row[0], Decimal(0)) / row[1]),
                -row[2],
            ),
        )
        required[ingredient_id] += quantity
    return dict(required), unquantified


@api_view(['GET'])
@permission_classes([AllowAny])
def ranked_recipes(request):
    """GET /api/recommendations/?count=3&exclude=1,2,3

    Score is derived live from stock in PostgreSQL, not a stored / ML model.
    Strictly local demo access; same user as the shopping and pantry APIs.
    """
    user = demo_user()
    try:
        count = int(request.query_params.get('count', '3'))
    except (ValueError, TypeError):
        count = 3
    count = min(10, max(1, count))
    excluded = {
        int(token) for token in request.query_params.get('exclude', '').split(',')[:30]
        if token.isdecimal()
    }

    now = timezone.now()
    soon_cutoff = now + timedelta(hours=48)
    available = defaultdict(lambda: Decimal(0))
    expiring = defaultdict(lambda: Decimal(0))
    batches = (PantryItem.objects.filter(
        user=user, status=PantryItem.Status.AVAILABLE, amount__gt=0
    ).select_related('product__ingredient'))
    for batch in batches:
        if batch.expires_at is not None and batch.expires_at <= now:
            continue
        ingredient_id = batch.product.ingredient_id
        available[ingredient_id] += batch.amount
        if batch.expires_at is not None and batch.expires_at <= soon_cutoff:
            expiring[ingredient_id] += batch.amount

    # A single prefetch for the cookbook avoids a query for every recipe.
    cookbook = (Recipe.objects.filter(owner__isnull=True)
                .exclude(id__in=excluded)
                .select_related('category')
                .prefetch_related('items__ingredient'))
    results = []
    for recipe in cookbook:
        required, ignored_count = _quantified_requirements(recipe, available)
        if not required:
            continue
        score = score_recipe(required, available, expiring)
        items = list(recipe.items.all())
        results.append({
            'id': recipe.pk,
            'name': recipe.name,
            'base_servings': recipe.base_servings,
            'category': recipe.category.name if recipe.category_id else None,
            'ingredients': list(dict.fromkeys(
                item.ingredient.canonical_name for item in items
            )),
            'score': score.total,
            'score_breakdown': {
                'availability': score.coverage,
                'few_missing': score.few_missing,
                'expiry': score.expiring,
            },
            'missing_ingredients_count': score.missing_count,
            'scored_ingredients_count': score.ingredient_count,
            'unquantified_ingredients_count': ignored_count,
        })

    results.sort(key=lambda item: (-item['score'], item['missing_ingredients_count'], item['id']))
    return Response({'results': results[:count], 'scoring': {
        'availability_max': 60, 'few_missing_max': 25, 'expiry_max': 15,
        'expiry_window_hours': 48,
        'has_pantry_stock': bool(available),
    }})
