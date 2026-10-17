from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from .validators import validate_profile_image


class UserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('Mobile number is required')
        user = self.model(mobile_number=mobile_number.strip(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active_member', True)
        extra_fields.setdefault('is_super_manager', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(mobile_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=100)
    is_super_manager = models.BooleanField(default=False)
    is_active_member = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(
        upload_to='profiles/', blank=True, null=True, validators=[validate_profile_image]
    )

    objects = UserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return f'{self.full_name} ({self.mobile_number})'

    @property
    def is_monthly_manager(self):
        return self.monthly_manager_assignments.filter(is_active=True).exists()

    @property
    def role_display(self):
        if self.is_super_manager:
            return 'Super Manager'
        if self.is_monthly_manager:
            return 'Monthly Manager'
        return 'Member'
