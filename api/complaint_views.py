from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.complaint_serializers import (
    ComplaintCreateSerializer,
    ComplaintSerializer,
    ComplaintStatusSerializer,
)
from api.permissions import IsActiveMember, IsMonthlyManagerOrAbove
from complaints.models import Complaint
from complaints.services import create_complaint, update_complaint_status


class ComplaintCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def post(self, request):
        serializer = ComplaintCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            complaint = create_complaint(request.user, **serializer.validated_data)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ComplaintSerializer(complaint).data, status=status.HTTP_201_CREATED)


class MyComplaintsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def get(self, request):
        complaints = Complaint.objects.filter(raised_by=request.user)
        return Response(ComplaintSerializer(complaints, many=True).data)


class AllComplaintsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]

    def get(self, request):
        complaints = Complaint.objects.select_related('raised_by', 'handled_by').all()
        return Response(ComplaintSerializer(complaints, many=True).data)


class ComplaintStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMonthlyManagerOrAbove]

    def patch(self, request, complaint_id):
        complaint = Complaint.objects.filter(pk=complaint_id).first()
        if not complaint:
            return Response({'detail': 'Complaint not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ComplaintStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            update_complaint_status(complaint, serializer.validated_data['status'], request.user)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ComplaintSerializer(complaint).data)
