"""Local demo shopping API, without login. Enable only in LTC_DEMO_MODE."""
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from pantry.models import PantryItem
from products.models import Product
from recipes.models import Recipe
from recommendations.models import PlannedMeal
from .repository import build_shopping_list
from .serializers import ShoppingLineSerializer
from users.demo import demo_user


class PlanRecipeSerializer(serializers.Serializer):
    recipe_id = serializers.IntegerField(min_value=1)
    servings = serializers.IntegerField(min_value=1, max_value=99)


class PurchaseSerializer(serializers.Serializer):
    ingredient_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def shopping_list_view(request):
    lines = build_shopping_list(demo_user())
    return Response(ShoppingLineSerializer(lines, many=True).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def plan_recipe_view(request):
    data = PlanRecipeSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    recipe = get_object_or_404(
        Recipe.objects.filter(owner__isnull=True), pk=data.validated_data['recipe_id']
    )
    meal = PlannedMeal.objects.create(
        user=demo_user(),
        recipe=recipe,
        servings=data.validated_data['servings'],
        planned_for=timezone.localdate(),
        status=PlannedMeal.Status.PLANNED,
    )
    return Response(
        {'id': meal.pk, 'recipe_id': recipe.pk, 'servings': meal.servings,
         'planned_for': meal.planned_for.isoformat()},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def purchase_view(request):
    data = PurchaseSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    user = demo_user()
    # The server calculates amounts; clients can only select currently missing items.
    missing = {line.ingredient.pk: line for line in build_shopping_list(user)}
    selected_ids = set(data.validated_data['ingredient_ids'])
    unknown = selected_ids - missing.keys()
    if unknown:
        raise ValidationError({'ingredient_ids': f'Nie ma na liście składników: {sorted(unknown)}'})
    for ingredient_id in selected_ids:
        line = missing[ingredient_id]
        product, _ = Product.objects.get_or_create(
            ingredient=line.ingredient,
            ean='',
            defaults={
                'full_name': line.ingredient.canonical_name,
                'package_amount': '',
                'normalised_amount': 1.0,
            },
        )
        PantryItem.objects.create(
            user=user, product=product, amount=line.to_buy,
            status=PantryItem.Status.AVAILABLE,
        )
    return Response({'added': len(selected_ids)})
