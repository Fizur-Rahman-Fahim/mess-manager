import os

from django.core.exceptions import ValidationError


MAX_PROFILE_SIZE = 2 * 1024 * 1024
ALLOWED_PROFILE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def validate_profile_image(image):
    if image is None:
        return
    if image.size > MAX_PROFILE_SIZE:
        raise ValidationError('Profile image must be 2 MB or smaller.')
    extension = os.path.splitext(image.name)[1].lower()
    if extension not in ALLOWED_PROFILE_EXTENSIONS:
        raise ValidationError('Profile image must be JPEG, PNG, or WebP.')
