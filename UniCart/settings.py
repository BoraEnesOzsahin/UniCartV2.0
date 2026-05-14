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

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'users.middleware.RequireEmailVerificationMiddleware',
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
# We prioritize individual DB_* variables for reliability (Supabase).
# We then check DATABASE_URL.
# Finally, we fall back to local SQLite.

db_name = os.getenv('DB_NAME')
if db_name:
    # Use individual variables (Safe for passwords with special chars)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,
        }
    }
else:
    # Use DATABASE_URL or SQLite
    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
            conn_max_age=600,
            conn_health_checks=True,
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

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', '')
if not EMAIL_BACKEND:
    if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# If you want to force SMTP delivery in development, set EMAIL_BACKEND in .env.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True
