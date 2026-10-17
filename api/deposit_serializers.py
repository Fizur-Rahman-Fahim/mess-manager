from decimal import Decimal

from rest_framework import serializers

from deposits.models import Deposit


class DepositSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_mobile = serializers.CharField(source='user.mobile_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Deposit
        fields = (
            'id',
            'user',
            'user_name',
            'user_mobile',
            'amount',
            'date_claimed',
            'status',
            'status_display',
            'approved_by',
            'approved_at',
            'note',
            'created_at',
        )
        read_only_fields = (
            'id',
            'user',
            'user_name',
            'user_mobile',
            'status',
            'status_display',
            'approved_by',
            'approved_at',
            'created_at',
        )


class DepositClaimSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    date_claimed = serializers.DateField()
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)
