from decimal import Decimal

from rest_framework import serializers

from expenses.models import BazarExpense


class BazarExpenseSerializer(serializers.ModelSerializer):
    bazar_type_display = serializers.CharField(source='get_bazar_type_display', read_only=True)
    added_by_name = serializers.CharField(source='added_by.full_name', read_only=True)
    receipt_image_url = serializers.SerializerMethodField()

    class Meta:
        model = BazarExpense
        fields = (
            'id',
            'bazar_type',
            'bazar_type_display',
            'amount',
            'date',
            'description',
            'month',
            'added_by',
            'added_by_name',
            'receipt_image',
            'receipt_image_url',
            'created_at',
        )
        read_only_fields = (
            'id',
            'month',
            'added_by',
            'added_by_name',
            'created_at',
            'receipt_image_url',
        )

    def get_receipt_image_url(self, obj):
        if obj.receipt_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt_image.url)
            return obj.receipt_image.url
        return None


class BazarExpenseCreateSerializer(serializers.Serializer):
    bazar_type = serializers.ChoiceField(choices=BazarExpense.BAZAR_TYPE_CHOICES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    date = serializers.DateField()
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    receipt_image = serializers.ImageField(required=False, allow_null=True)
