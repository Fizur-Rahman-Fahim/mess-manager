from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.deposit_serializers import DepositClaimSerializer, DepositSerializer
from api.permissions import IsActiveMember, IsMonthlyManagerOrAbove
from deposits.models import Deposit
from deposits.services.deposit import (
    approve_deposit,
    claim_deposit,
    get_pending_deposits,
    get_user_deposits,
    reject_deposit,
)
from meals.services.meal import current_month_str


class DepositClaimAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def post(self, request):
        serializer = DepositClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            deposit = claim_deposit(
                request.user,
                data['amount'],
                data['date_claimed'],
                data.get('note', ''),
            )
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DepositSerializer(deposit).data, status=status.HTTP_201_CREATED)


class MyDepositsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def get(self, request):
        month = request.query_params.get('month')
        try:
            deposits = get_user_deposits(request.user, month)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DepositSerializer(deposits, many=True)
        return Response(
            {
                'month': month or current_month_str(),
                'deposits': serializer.data,
            }
        )


class PendingDepositsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]

    def get(self, request):
        deposits = get_pending_deposits()
        serializer = DepositSerializer(deposits, many=True)
        return Response({'deposits': serializer.data})


class ApproveDepositAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]

    def post(self, request, deposit_id):
        deposit = Deposit.objects.filter(pk=deposit_id, status=Deposit.STATUS_PENDING).first()
        if not deposit:
            return Response({'detail': 'Pending deposit not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            approve_deposit(deposit, request.user)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DepositSerializer(deposit).data)


class RejectDepositAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]

    def post(self, request, deposit_id):
        deposit = Deposit.objects.filter(pk=deposit_id, status=Deposit.STATUS_PENDING).first()
        if not deposit:
            return Response({'detail': 'Pending deposit not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            reject_deposit(deposit, request.user)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DepositSerializer(deposit).data)
