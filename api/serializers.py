from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role_display', read_only=True)
    is_monthly_manager = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'mobile_number',
            'full_name',
            'is_active_member',
            'is_super_manager',
            'is_monthly_manager',
            'role',
            'date_joined',
            'profile_photo',
        )
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        mobile = attrs['mobile_number'].strip()
        user = authenticate(
            request=self.context.get('request'),
            username=mobile,
            password=attrs['password'],
        )
        if not user:
            raise serializers.ValidationError('Invalid mobile number or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account is disabled.')
        attrs['user'] = user
        return attrs
