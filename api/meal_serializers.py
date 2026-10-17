from rest_framework import serializers

from meals.models import DailyMeal


class DailyMealSerializer(serializers.ModelSerializer):
    total_meal_value = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = DailyMeal
        fields = (
            'id',
            'date',
            'breakfast',
            'lunch',
            'dinner',
            'total_meal_value',
            'can_edit',
        )

    def get_total_meal_value(self, obj):
        return str(obj.total_meal_value())

    def get_can_edit(self, obj):
        from meals.services.meal import can_modify_date

        return can_modify_date(obj.date)


class MealToggleSerializer(serializers.Serializer):
    date = serializers.DateField()
    breakfast = serializers.BooleanField()
    lunch = serializers.BooleanField()
    dinner = serializers.BooleanField()


class MealSummarySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    full_name = serializers.CharField()
    mobile_number = serializers.CharField()
    breakfast_count = serializers.IntegerField()
    lunch_count = serializers.IntegerField()
    dinner_count = serializers.IntegerField()
    total_meal_value = serializers.DecimalField(max_digits=10, decimal_places=2)
