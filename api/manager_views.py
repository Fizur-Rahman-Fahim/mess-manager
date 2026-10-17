from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsSuperManager
from api.settings_serializers import ManagerAssignmentSerializer
from mess_core.models import MonthlyManagerAssignment
from mess_core.services.manager import assign_monthly_manager, get_active_manager


class ManagerAssignmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperManager]

    def get(self, request):
        active = get_active_manager()
        history = MonthlyManagerAssignment.objects.select_related('user').all()[:20]
        return Response({
            'active': self._serialize(active),
            'history': [self._serialize(assignment) for assignment in history],
        })

    def post(self, request):
        serializer = ManagerAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            assignment = assign_monthly_manager(
                serializer.validated_data['user_id'],
                serializer.validated_data['month'],
                assigned_by=request.user,
            )
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self._serialize(assignment), status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(assignment):
        if not assignment:
            return None
        return {
            'id': assignment.id,
            'user_id': assignment.user_id,
            'full_name': assignment.user.full_name,
            'mobile_number': assignment.user.mobile_number,
            'month': assignment.month,
            'is_active': assignment.is_active,
            'start_date': assignment.start_date,
            'end_date': assignment.end_date,
        }
