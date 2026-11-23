"""Pantry CRUD for the local single-user LTC demo, using the same stock as shopping."""
from datetime import datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from products.models import Product
from recipes.models import Ingredient
from users.demo import demo_user
from .models import PantryItem


class PantryWriteSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField(min_value=1, required=False)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=4, min_value=Decimal('0.0001'), required=False,
    )
    expires_on = serializers.DateField(required=False, allow_null=True)


PANTRY_TIMEZONE = ZoneInfo("Europe/Warsaw")


def expiry_to_datetime(date_value):
    if date_value is None:
        return None
    # A date on the label is valid until the end of that calendar day.
    return timezone.make_aware(datetime.combine(date_value, time.max), PANTRY_TIMEZONE)


def serialize_item(item):
    ingredient = item.product.ingredient
    expiry = timezone.localtime(item.expires_at, PANTRY_TIMEZONE).date() if item.expires_at else None
    if item.expires_at is None:
        expiry_status = 'none'
    elif item.expires_at <= timezone.now():
        expiry_status = 'expired'
    elif item.expires_at <= timezone.now() + timedelta(hours=48):
        expiry_status = 'soon'
    else:
        expiry_status = 'fresh'
    return {
        'id': item.pk,
        'ingredient_id': ingredient.pk,
        'ingredient_name': ingredient.canonical_name,
        'product_name': item.product.full_name,
        'amount': str(item.amount),
        'unit': ingredient.base_unit,
        'expires_on': expiry.isoformat() if expiry else None,
        'expiry_status': expiry_status,
    }


def generic_product(ingredient):
    product, _ = Product.objects.get_or_create(
        ingredient=ingredient, ean='',
        defaults={
            'full_name': ingredient.canonical_name,
            'package_amount': '',
            'normalised_amount': 1.0,
        },
    )
    return product


@api_view(['GET'])
@permission_classes([AllowAny])
def pantry_ingredients(request):
    demo_user()
    ingredients = Ingredient.objects.order_by('canonical_name').values(
        'id', 'canonical_name', 'base_unit'
    )
    return Response([
        {'id': ingredient['id'], 'name': ingredient['canonical_name'], 'unit': ingredient['base_unit']}
        for ingredient in ingredients
    ])


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@transaction.atomic
def pantry_list_create(request):
    user = demo_user()
    if request.method == 'GET':
        items = PantryItem.objects.filter(
            user=user, status=PantryItem.Status.AVAILABLE,
        ).select_related('product__ingredient').order_by('expires_at', '-added_at', 'pk')
        return Response([serialize_item(item) for item in items])

    serializer = PantryWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    values = serializer.validated_data
    if 'ingredient_id' not in values or 'amount' not in values:
        raise serializers.ValidationError({'detail': 'Wybierz składnik i podaj ilość.'})
    ingredient = get_object_or_404(Ingredient, pk=values['ingredient_id'])
    item = PantryItem.objects.create(
        user=user,
        product=generic_product(ingredient),
        amount=values['amount'],
        expires_at=expiry_to_datetime(values.get('expires_on')),
    )
    return Response(serialize_item(item), status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([AllowAny])
@transaction.atomic
def pantry_item_detail(request, item_id):
    user = demo_user()
    item = get_object_or_404(
        PantryItem.objects.select_related('product__ingredient'),
        pk=item_id, user=user, status=PantryItem.Status.AVAILABLE,
    )
    if request.method == 'DELETE':
        # Preserve history for future waste statistics; remove it from active stock.
        item.status = PantryItem.Status.DISCARDED
        item.finished_at = timezone.now()
        item.save(update_fields=['status', 'finished_at'])
        return Response({'removed': True})

    serializer = PantryWriteSerializer(data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    values = serializer.validated_data
    if not values:
        raise serializers.ValidationError({'detail': 'Nie podano zmian.'})
    fields = []
    if 'ingredient_id' in values:
        ingredient = get_object_or_404(Ingredient, pk=values['ingredient_id'])
        item.product = generic_product(ingredient)
        fields.append('product')
    if 'amount' in values:
        item.amount = values['amount']
        fields.append('amount')
    if 'expires_on' in values:
        item.expires_at = expiry_to_datetime(values['expires_on'])
        fields.append('expires_at')
    item.save(update_fields=fields)
    return Response(serialize_item(item))
