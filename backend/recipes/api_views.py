"""Public, read-only JSON endpoints for the LTC cookbook.

This is a small first integration with Next.js; private user recipes and write
operations will need authenticated endpoints in a separate change.
"""
import re

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from .models import Recipe


def _summary(recipe):
    return {
        "id": recipe.id,
        "name": recipe.name,
        "base_servings": recipe.base_servings,
        "category": recipe.category.name if recipe.category_id else None,
    }


def _decimal(value):
    return str(value) if value is not None else None


@require_GET
def recipe_list(request):
    # Never expose user-owned private recipes from this public endpoint.
    recipes = (Recipe.objects.filter(owner__isnull=True)
               .select_related("category")
               .order_by("id"))

    query = request.GET.get("q", "").strip()[:100]
    if query:
        # PostgreSQL \m means 'start of a word'. Unlike icontains, this
        # matches 'zupa' but not the embedded 'zupa' inside 'szczupak'.
        # Each token may occur in the recipe title OR an ingredient name.
        for term in query.split():
            word_prefix = r"\m" + re.escape(term)
            recipes = recipes.filter(
                Q(name__iregex=word_prefix)
                | Q(items__ingredient__canonical_name__iregex=word_prefix)
            )
        recipes = recipes.distinct()

    paginator = Paginator(recipes, 20)
    page = paginator.get_page(request.GET.get("page", "1"))
    return JsonResponse({
        "count": paginator.count,
        "page": page.number,
        "pages": paginator.num_pages,
        "results": [_summary(recipe) for recipe in page.object_list],
    })


@require_GET
def recipe_suggestions(request):
    """Random public cookbook recipes for the homepage (not a saved meal plan)."""
    try:
        count = int(request.GET.get("count", "3"))
    except ValueError:
        count = 3
    count = max(1, min(count, 10))

    # Keep exclusions bounded and ignore malformed IDs from the client.
    excluded = [
        int(item) for item in request.GET.get("exclude", "").split(",")[:30]
        if item.isdecimal()
    ]
    recipes = (
        Recipe.objects.filter(owner__isnull=True)
        .exclude(pk__in=excluded)
        .prefetch_related("items__ingredient")
        .order_by("?")[:count]
    )
    return JsonResponse({
        "results": [
            {
                **_summary(recipe),
                "ingredients": list(dict.fromkeys(
                    item.ingredient.canonical_name for item in recipe.items.all()
                )),
            }
            for recipe in recipes
        ]
    })


@require_GET
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.filter(owner__isnull=True)
        .select_related("category")
        .prefetch_related("items__ingredient"),
        pk=recipe_id,
    )
    return JsonResponse({
        **_summary(recipe),
        "steps": recipe.steps,
        "items": [
            {
                "id": item.id,
                "ingredient": item.ingredient.canonical_name,
                "amount": _decimal(item.amount),
                "amount_max": _decimal(item.amount_max),
                "unit": item.ingredient.base_unit,
                "quantity_note": item.quantity_note,
                "group": item.group,
                "alternative_group": item.alternative_group,
                "is_optional": item.is_optional,
            }
            for item in recipe.items.all()
        ],
    })
