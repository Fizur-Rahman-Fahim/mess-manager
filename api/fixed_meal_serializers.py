from decimal import Decimal

from rest_framework import serializers


class FixedMealSerializer(serializers.Serializer):
    month = serializers.RegexField(regex=r'^\d{4}-\d{2}$')
    fixed_meal_count = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0'))
