from decimal import Decimal

from rest_framework import serializers

from mess_core.models import MessSettings


class MessSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessSettings
        fields = (
            'seat_bill_default',
            'current_bill_default',
            'breakfast_meal_value',
            'lunch_meal_value',
            'dinner_meal_value',
            'meal_off_cutoff_time',
            'updated_by',
            'updated_at',
        )
        read_only_fields = ('updated_by', 'updated_at')

    def validate(self, attrs):
        for field in ('seat_bill_default', 'current_bill_default'):
            if attrs.get(field, Decimal('0')) < 0:
                raise serializers.ValidationError({field: 'Value cannot be negative.'})
        for field in ('breakfast_meal_value', 'lunch_meal_value', 'dinner_meal_value'):
            if attrs.get(field, Decimal('0')) < 0:
                raise serializers.ValidationError({field: 'Meal value cannot be negative.'})
        return attrs


class ManagerAssignmentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    month = serializers.RegexField(regex=r'^\d{4}-\d{2}$')
