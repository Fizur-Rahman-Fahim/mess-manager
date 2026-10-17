from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsActiveMember, IsSuperManager
from api.settings_serializers import MessSettingsSerializer
from meals.services.meal import get_mess_settings


class SettingsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveMember]

    def get(self, request):
        return Response(MessSettingsSerializer(get_mess_settings()).data)

    def patch(self, request):
        if not IsSuperManager().has_permission(request, self):
            return Response({'detail': IsSuperManager.message}, status=status.HTTP_403_FORBIDDEN)

        settings_obj = get_mess_settings()
        serializer = MessSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)
