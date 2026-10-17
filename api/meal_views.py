from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.meal_serializers import DailyMealSerializer, MealSummarySerializer, MealToggleSerializer
from api.permissions import IsActiveMember, IsMonthlyManagerOrAbove
from meals.services.meal import (
    current_month_str,
    get_daily_meal_summary,
    get_monthly_summary,
    get_user_meals_for_month,
    toggle_meals,
)


class MyMealsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def get(self, request):
        month = request.query_params.get('month', current_month_str())
        try:
            meals = get_user_meals_for_month(request.user, month)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DailyMealSerializer(meals, many=True)
        return Response({'month': month, 'meals': serializer.data})


class MealToggleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def post(self, request):
        serializer = MealToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            meal = toggle_meals(
                request.user,
                data['date'],
                data['breakfast'],
                data['lunch'],
                data['dinner'],
            )
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DailyMealSerializer(meal).data)


class MealSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]

    def get(self, request):
        month = request.query_params.get('month', current_month_str())
        try:
            summary = get_monthly_summary(month)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MealSummarySerializer(summary, many=True)
        return Response({'month': month, 'members': serializer.data})


class DailyMealSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]

    def get(self, request):
        month = request.query_params.get('month', current_month_str())
        try:
            daily_summary = get_daily_meal_summary(month)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'month': month, 'days': daily_summary})
