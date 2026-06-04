from pathlib import Path
import os
import dj_database_url
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

# ─────────────────────────────────────────
#  SETTINGS.PY  — project configuration
# ─────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# Add 'apps' to sys.path
import sys
sys.path.append(str(BASE_DIR / 'apps'))

# Load environment variables from .env file
if load_dotenv:
    load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'replace-this-with-a-real-secret-key-before-deployment')

IS_VERCEL = bool(os.getenv('VERCEL')) or bool(os.getenv('VERCEL_URL')) or bool(os.getenv('VERCEL_ENV'))

DEBUG_DEFAULT = 'False' if IS_VERCEL else 'True'
DEBUG = os.getenv('DEBUG', DEBUG_DEFAULT).lower() in ('1', 'true', 'yes', 'on')

# Comma-separated, e.g. "localhost,127.0.0.1,.vercel.app".
ALLOWED_HOSTS_DEFAULT = 'localhost,127.0.0.1,.vercel.app' if IS_VERCEL else 'localhost,127.0.0.1'
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', ALLOWED_HOSTS_DEFAULT).split(',')
    if host.strip()
]

# Vercel provides the deployment URL without scheme (e.g. "my-app.vercel.app").
vercel_url = os.getenv('VERCEL_URL')
if vercel_url and vercel_url not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(vercel_url)


# ── Apps ──────────────────────────────────
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps ↓ (add them here after running startapp)
    'core',
    'listings',
    'users',
    'chats',
    'channels',
]

ASGI_APPLICATION = 'UniCart.asgi.application'

import logging

# Channel layer config: use Redis when REDIS_URL is provided, otherwise in-memory (single instance)
if os.getenv('REDIS_URL'):
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [os.getenv('REDIS_URL')],
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Basic logger for ASGI / Channels troubleshooting
logging.getLogger('django.channels').addHandler(logging.NullHandler())

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'users.middleware.RequireEmailVerificationMiddleware',  # ← BAŞINA # KOYARAK İPTAL EDİN
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'UniCart.urls'


# ── Templates ─────────────────────────────
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],    # ← tells Django where to find your HTML files
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'users.context_processors.email_verification_status',
            'chats.context_processors.unread_chat_count',
        ],
    },
}]


# ── Database ──────────────────────────────
# Eğer Render üzerinde DATABASE_URL tanımlıysa Supabase'e bağlan,
# yoksa build sırasında sqlite kullan ki deploy aşamasında hata yaşanmasın.
DATABASE_URL = os.getenv('DATABASE_URL')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_SSL_MODE = os.getenv('DB_SSL_MODE', 'require')

if DB_HOST and DB_NAME and DB_USER and DB_PASSWORD:
    database_url = (
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        f'?sslmode={DB_SSL_MODE}'
    )
else:
    database_url = DATABASE_URL

DATABASES = {
    'default': dj_database_url.config(
        default=database_url or 'sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=30,
        ssl_require=True,
    )
}


# ── Static files (CSS, JS, images) ────────
STATIC_URL  = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']   # your static/ folder

# ── Media files (user uploads) ────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'            # uploaded images saved here


# ── Auth redirects ─────────────────────────
LOGIN_URL          = '/users/login/'        # where @login_required sends non-logged-in users
LOGIN_REDIRECT_URL = '/'                   # where to go after successful login
LOGOUT_REDIRECT_URL = '/'

# ── Email Configuration ───────────────────
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp-mail.outlook.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@unicart.local')

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', '')
SUPABASE_DB_SSL_MODE = os.getenv('DB_SSL_MODE', 'require')

# Proje Render'da (canlıda) çalışırken mailleri göndermek yerine loglara yazar, böylece kilitlenme yaşanmaz.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_USE_TLS = True  
EMAIL_FAIL_SILENTLY = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- Security: proxy / cookie settings for production (Render, Heroku, etc.)
# Let Django know it's behind a proxy that sets X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Secure cookies in non-debug (production) environments
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# CSRF trusted origins: allow explicit env var or derive from ALLOWED_HOSTS
# For Django >=4.0 this must include scheme (https://example.onrender.com)
raw_trusted = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if raw_trusted:
    CSRF_TRUSTED_ORIGINS = [s.strip() for s in raw_trusted.split(',') if s.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []
    for h in ALLOWED_HOSTS:
        if h and h not in ('localhost', '127.0.0.1'):
            # prefer https
            if h.startswith('http://') or h.startswith('https://'):
                CSRF_TRUSTED_ORIGINS.append(h)
            else:
                CSRF_TRUSTED_ORIGINS.append(f'https://{h}')
