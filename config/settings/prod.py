import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = False

if os.environ.get('SECRET_KEY', '').strip() in {'', 'change-me-in-production', 'django-insecure-dev-only-change-in-production'}:
    raise RuntimeError('A production SECRET_KEY environment variable is required.')

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# Render's health check calls this path without HTTPS headers.
SECURE_REDIRECT_EXEMPT = [r'^healthz/$']

# Render injects the public hostname; trust it for Host and CSRF (needed for /admin/ over HTTPS).
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:  # noqa: F405
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)  # noqa: F405
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']
