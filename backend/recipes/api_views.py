"""Public, read-only JSON endpoints for the LTC cookbook.

This is a small first integration with Next.js; private user recipes and write
operations will need authenticated endpoints in a separate change.
"""
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from .models import Recipe


def _summary(recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "servings": recipe.servings,
        "source_number": recipe.source_number,
        "parsing_status": recipe.parsing_status,
        "category": recipe.category.name if recipe.category_id else None,
        "cookbook": str(recipe.cookbook) if recipe.cookbook_id else None,
    }


@require_GET
def recipe_list(request):
    # Never expose user-owned private recipes from this public endpoint.
    recipes = (Recipe.objects.filter(owner__isnull=True)
               .select_related("category", "cookbook")
               .order_by("id"))

    query = request.GET.get("q", "").strip()[:100]
    if query:
        recipes = recipes.filter(title__icontains=query)

    paginator = Paginator(recipes, 20)
    page = paginator.get_page(request.GET.get("page", "1"))
    return JsonResponse({
        "count": paginator.count,
        "page": page.number,
        "pages": paginator.num_pages,
        "results": [_summary(recipe) for recipe in page.object_list],
    })


@require_GET
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.filter(owner__isnull=True)
        .select_related("category", "cookbook")
        .prefetch_related("items__ingredient"),
        pk=recipe_id,
    )
    return JsonResponse({
        **_summary(recipe),
        "instructions": recipe.instructions,
        "raw_ingredients": recipe.raw_ingredients,
        "items": [
            {
                "id": item.id,
                "position": item.position,
                "raw_text": item.raw_text,
                "ingredient": item.ingredient.name if item.ingredient_id else None,
                "amount": str(item.amount) if item.amount is not None else None,
                "amount_max": str(item.amount_max) if item.amount_max is not None else None,
                "unit": item.unit,
            }
            for item in recipe.items.all()
        ],
    })
