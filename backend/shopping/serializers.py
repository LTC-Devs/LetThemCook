from rest_framework import serializers

class ShoppingLineSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField(source="ingredient.id")
    ingredient_name = serializers.CharField(source="ingredient.canonical_name")
    unit = serializers.CharField()
    needed = serializers.DecimalField(max_digits=12, decimal_places=4)
    in_stock = serializers.DecimalField(max_digits=12, decimal_places=4)
    to_buy = serializers.DecimalField(max_digits=12, decimal_places=4)