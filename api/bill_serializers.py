from decimal import Decimal

from rest_framework import serializers

from bills.models import MonthlyBillCycle, UserBillRecord


class MonthlyBillCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyBillCycle
        fields = (
            'month',
            'house_rent_total',
            'house_rent_paid',
            'electricity_bill_total',
            'electricity_bill_paid',
            'total_meal_count',
            'meal_rate',
            'updated_at',
        )


class UserBillRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_mobile = serializers.CharField(source='user.mobile_number', read_only=True)

    class Meta:
        model = UserBillRecord
        fields = (
            'id',
            'user',
            'user_name',
            'user_mobile',
            'month',
            'seat_bill',
            'current_bill_share',
            'house_rent_share',
            'electricity_share',
            'meal_cost',
            'total_due',
            'total_deposit',
            'balance',
        )


class MonthAmountSerializer(serializers.Serializer):
    month = serializers.RegexField(regex=r'^\d{4}-\d{2}$')
    total = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))
    paid = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0'),
        required=False,
        default=Decimal('0'),
    )


class GenerateBillSerializer(serializers.Serializer):
    month = serializers.RegexField(regex=r'^\d{4}-\d{2}$')
