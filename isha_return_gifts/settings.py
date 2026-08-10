import os
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# ── CORE ──────────────────────────────────
# All three MUST come from the environment. No production-unsafe defaults:
# a missing SECRET_KEY should crash the deploy, not silently ship a known key.
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

# Render assigns a *.onrender.com subdomain that isn't known until the first
# deploy, so it can't be hardcoded into ALLOWED_HOSTS beforehand. Render sets
# this env var on every web service automatically — pick it up as a safety net
# on top of whatever ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS were already set to.
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if _render_host:
    ALLOWED_HOSTS.append(_render_host)
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'products',
    'dashboard',
    'orders',
    'payments',
    'users',
    'contact',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must sit directly after SecurityMiddleware so static files are
    # served without running the rest of the stack.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'isha_return_gifts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'isha_return_gifts.wsgi.application'

# ── DATABASE ──────────────────────────────
# SQLite locally; set DATABASE_URL to a Postgres URL (e.g. Supabase) in
# production. Use the DIRECT connection string (port 5432), not the pgbouncer
# transaction pooler — this app runs on a persistent process (gunicorn on a
# normal host), not serverless, so Django's own connection reuse below is the
# right tool and the pooler's transaction-mode caveats don't apply.
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            # Supabase requires TLS; this fails fast if a pasted URL omits it
            # rather than silently connecting in plaintext.
            ssl_require=True,
        ),
    }
    # Detects a connection Supabase has dropped for being idle (it recycles
    # them periodically) and opens a fresh one instead of reusing a dead one.
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── STATIC & MEDIA ────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Product/category/testimonial images. Filesystem storage locally; Supabase
# Storage (S3-compatible) when the three vars below are set. Gated so a
# developer without a Supabase project still gets a fully working site.
SUPABASE_S3_ENDPOINT = config('SUPABASE_S3_ENDPOINT', default='')
SUPABASE_S3_ACCESS_KEY = config('SUPABASE_S3_ACCESS_KEY', default='')
SUPABASE_S3_SECRET_KEY = config('SUPABASE_S3_SECRET_KEY', default='')
USE_SUPABASE_STORAGE = bool(
    SUPABASE_S3_ENDPOINT and SUPABASE_S3_ACCESS_KEY and SUPABASE_S3_SECRET_KEY
)

# urls.py references MEDIA_URL/MEDIA_ROOT unconditionally (they're harmless
# when unused: static() only serves files when DEBUG=True, and S3Storage
# builds each file's actual URL from the bucket, not from MEDIA_URL).
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if USE_SUPABASE_STORAGE:
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'bucket_name': config('SUPABASE_S3_BUCKET', default='media'),
                'endpoint_url': SUPABASE_S3_ENDPOINT,
                'access_key': SUPABASE_S3_ACCESS_KEY,
                'secret_key': SUPABASE_S3_SECRET_KEY,
                'region_name': config('SUPABASE_S3_REGION', default='ap-south-1'),
                # Supabase's S3 gateway rejects the ACL parameter boto3 sends
                # by default; bucket-level "public" access is set once in the
                # Supabase dashboard instead.
                'default_acl': None,
                # No signed query-string auth: product photos are public, and
                # signed URLs would break far-future cache headers.
                'querystring_auth': False,
                'file_overwrite': False,
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'

# ── SECURITY (production only) ────────────
# These break local http:// development, so they switch on with DEBUG=False.
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'
    # Most PaaS hosts (Railway, Render, Heroku) terminate TLS at a proxy and
    # forward the original scheme in this header.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── RAZORPAY ──────────────────────────────
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')

# Escape hatch for dev machines behind a TLS-intercepting proxy, where outbound
# HTTPS to the Razorpay API fails with CERTIFICATE_VERIFY_FAILED. Disabling
# verification exposes the payment API calls to man-in-the-middle attacks, so it
# is opt-in AND gated on DEBUG — it can never activate in production.
if DEBUG and config('DISABLE_SSL_VERIFY', default=False, cast=bool):
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

# ── EMAIL (Gmail SMTP) ────────────────────
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# Mail is still sent inside the request, so an unresponsive SMTP server would
# otherwise hold the connection open until gunicorn's own timeout fires.
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)
# Gmail rewrites the From header to the authenticated account, so this should
# match EMAIL_HOST_USER or mail will be rejected/rewritten.
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
ADMIN_EMAIL = config('ADMIN_EMAIL', default='')

# No real mailbox configured yet: fall back to the console backend, which
# "sends" mail by printing it to the server log instead of opening a real SMTP
# connection. Without this, the placeholder value in .env.example (or a blank
# EMAIL_HOST_USER) makes every send attempt a real, failing connection to
# Gmail — an auth error today, and it was a CERTIFICATE_VERIFY_FAILED before
# DISABLE_SSL_VERIFY existed. Swap in a real EMAIL_HOST_USER/PASSWORD later
# and this switches to actually sending, with no other code change needed.
_EMAIL_CONFIGURED = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD) and not EMAIL_HOST_USER.startswith('your_')
EMAIL_BACKEND = (
    'django.core.mail.backends.smtp.EmailBackend' if _EMAIL_CONFIGURED
    else 'django.core.mail.backends.console.EmailBackend'
)

# ── LOGGING ───────────────────────────────
# With DEBUG=False Django emails admins on 500s by default; log to stdout
# instead so the host's log viewer captures tracebacks.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
