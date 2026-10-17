import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_RECEIPT_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_RECEIPT_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def validate_receipt_image(image):
    if image is None:
        return

    if image.size > MAX_RECEIPT_SIZE:
        raise ValidationError(_('Receipt image must be 2 MB or smaller.'))

    ext = os.path.splitext(image.name)[1].lower()
    if ext not in ALLOWED_RECEIPT_EXTENSIONS:
        raise ValidationError(_('Receipt must be JPEG, PNG, or WebP.'))
