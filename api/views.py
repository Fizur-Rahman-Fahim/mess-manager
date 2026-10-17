from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.forms import UserRegistrationForm
from api.permissions import IsActiveMember, IsSuperManager
from api.serializers import LoginSerializer, UserSerializer

User = get_user_model()


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        form = UserRegistrationForm(data=request.data)
        if form.is_valid():
            user = form.save()
            return Response(
                {
                    'message': 'Registration submitted. Await Super Manager approval.',
                    'mobile_number': user.mobile_number,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if not user.is_superuser and not user.is_super_manager and not user.is_active_member:
            return Response(
                {'detail': 'Account pending approval.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
            }
        )


class MeAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PendingApprovalAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSuperManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(is_active_member=False, is_superuser=False).order_by('date_joined')


class ApproveUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperManager]

    def post(self, request, user_id):
        user = User.objects.filter(pk=user_id, is_active_member=False, is_superuser=False).first()
        if not user:
            return Response({'detail': 'User not found or already approved.'}, status=status.HTTP_404_NOT_FOUND)

        from accounts.services.member import approve_member

        approve_member(user, approved_by=request.user)
        return Response(UserSerializer(user).data)
