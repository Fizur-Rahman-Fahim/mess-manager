from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.bill_serializers import (
    GenerateBillSerializer,
    MonthAmountSerializer,
    MonthlyBillCycleSerializer,
    UserBillRecordSerializer,
)
from api.permissions import IsActiveMember, IsMonthlyManagerOrAbove, IsSuperManager
from bills.services.bill import (
    generate_bills,
    get_cycle,
    get_user_bill,
    set_electricity,
    set_house_rent,
)
from meals.services.meal import current_month_str


class MyBillAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def get(self, request):
        month = request.query_params.get('month', current_month_str())
        try:
            bill = get_user_bill(request.user, month)
            cycle = get_cycle(month)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        if not bill:
            return Response(
                {
                    'month': month,
                    'bill': None,
                    'cycle': MonthlyBillCycleSerializer(cycle).data if cycle else None,
                    'detail': 'Bill not generated yet for this month.',
                }
            )

        return Response(
            {
                'month': month,
                'bill': UserBillRecordSerializer(bill).data,
                'cycle': MonthlyBillCycleSerializer(cycle).data if cycle else None,
            }
        )


class SetHouseRentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperManager]

    def post(self, request):
        serializer = MonthAmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            cycle = set_house_rent(
                data['month'],
                data['total'],
                data.get('paid', 0),
                set_by=request.user,
            )
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MonthlyBillCycleSerializer(cycle).data)


class SetElectricityAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperManager]

    def post(self, request):
        serializer = MonthAmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            cycle = set_electricity(
                data['month'],
                data['total'],
                data.get('paid', 0),
                set_by=request.user,
            )
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MonthlyBillCycleSerializer(cycle).data)


class GenerateBillsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]

    def post(self, request):
        serializer = GenerateBillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        month = serializer.validated_data['month']

        try:
            cycle = generate_bills(month, generated_by=request.user)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MonthlyBillCycleSerializer(cycle).data, status=status.HTTP_201_CREATED)
