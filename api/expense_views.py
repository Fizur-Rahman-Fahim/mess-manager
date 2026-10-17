from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.expense_serializers import BazarExpenseCreateSerializer, BazarExpenseSerializer
from api.permissions import IsMonthlyManagerOrAbove
from expenses.services.expense import add_bazar_expense, get_monthly_expense_summary
from meals.services.meal import current_month_str


class BazarExpenseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        month = request.query_params.get('month', current_month_str())
        try:
            summary = get_monthly_expense_summary(month)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        expenses = BazarExpenseSerializer(
            summary['expenses'],
            many=True,
            context={'request': request},
        )
        return Response(
            {
                'month': summary['month'],
                'expenses': expenses.data,
                'boro_total': str(summary['boro_total']),
                'choto_total': str(summary['choto_total']),
                'total_bazar': str(summary['total_bazar']),
                'total_meal_count': str(summary['total_meal_count']),
                'meal_rate': str(summary['meal_rate']),
            }
        )

    def post(self, request):
        serializer = BazarExpenseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            expense = add_bazar_expense(
                request.user,
                data['bazar_type'],
                data['amount'],
                data['date'],
                data.get('description', ''),
                data.get('receipt_image'),
            )
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            BazarExpenseSerializer(expense, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
