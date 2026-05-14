from pathlib import Path
import os
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

# ─────────────────────────────────────────
#  SETTINGS.PY  — project configuration
# ─────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps ↓ (add them here after running startapp)
    'listings',
    'users',
    'marketplace',
]

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
        ],
    },
}]


# ── Database ──────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',   # local file-based DB, fine for development
    }
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
# Development: Console backend (prints emails to terminal)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@unicart.local')

# Outlook SMTP Config (for production):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp-mail.outlook.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True
