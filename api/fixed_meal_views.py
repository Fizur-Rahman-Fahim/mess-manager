from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.fixed_meal_serializers import FixedMealSerializer
from api.permissions import IsActiveMember, IsMonthlyManagerOrAbove
from mess_core.services.fixed_meal import get_fixed_meal, set_fixed_meal


class FixedMealAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def get(self, request):
        month = request.query_params.get('month')
        if not month:
            return Response({'detail': 'month is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fixed_meal = get_fixed_meal(month)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'month': month,
            'fixed_meal_count': fixed_meal.fixed_meal_count if fixed_meal else 0,
        })

    def post(self, request):
        if not IsMonthlyManagerOrAbove().has_permission(request, self):
            return Response({'detail': IsMonthlyManagerOrAbove.message}, status=status.HTTP_403_FORBIDDEN)
        serializer = FixedMealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            fixed_meal = set_fixed_meal(
                serializer.validated_data['month'],
                serializer.validated_data['fixed_meal_count'],
                set_by=request.user,
            )
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'month': fixed_meal.month,
            'fixed_meal_count': fixed_meal.fixed_meal_count,
        }, status=status.HTTP_201_CREATED)
