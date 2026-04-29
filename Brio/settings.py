import os
from pathlib import Path
import environ

from django.contrib.messages import constants as messages

# -------------------------
# BASE DIRECTORY
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# ENVIRONMENT
# -------------------------
env = environ.Env()
# Read .env file if it exists (optional for local development)
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# -------------------------
# SECURITY
# -------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or "dev-secret-key"
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Allow Railway domains and custom domains
ALLOWED_HOSTS = [
    ".railway.app",  # Matches all *.railway.app subdomains
    "localhost",
    "127.0.0.1",
]

# Add Railway's public domain if provided
if "RAILWAY_PUBLIC_DOMAIN" in os.environ:
    ALLOWED_HOSTS.append(os.environ["RAILWAY_PUBLIC_DOMAIN"])

# Allow custom domain from environment if set
if "ALLOWED_HOST" in os.environ:
    ALLOWED_HOSTS.append(os.environ["ALLOWED_HOST"])

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024      # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024      # 50MB

# -------------------------
# CSRF & SESSION COOKIES
# -------------------------
# CSRF trusted origins - Railway domains
CSRF_TRUSTED_ORIGINS = []

# Add Railway's public domain if provided
if "RAILWAY_PUBLIC_DOMAIN" in os.environ:
    domain = os.environ["RAILWAY_PUBLIC_DOMAIN"]
    CSRF_TRUSTED_ORIGINS.append(f"https://{domain}")

# Add Railway URL if provided
if "RAILWAY_STATIC_URL" in os.environ:
    CSRF_TRUSTED_ORIGINS.append(os.environ["RAILWAY_STATIC_URL"])

# For local development
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------
# LOGIN SETTINGS
# -------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

# -------------------------
# MESSAGE TAGS
# -------------------------
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# -------------------------
# INSTALLED APPS
# -------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "home",
    "django.contrib.humanize",
]

# -------------------------
# MIDDLEWARE
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------
# URL CONFIGURATION
# -------------------------
ROOT_URLCONF = "Brio.urls"

# -------------------------
# TEMPLATES
# -------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------------------------
# WSGI
# -------------------------
WSGI_APPLICATION = "Brio.wsgi.application"

# -------------------------
# DATABASE
# -------------------------
# Use SQLite database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------
# PASSWORD VALIDATION
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -------------------------
# INTERNATIONALIZATION
# -------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------
# STATIC FILES
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------
# MEDIA FILES (Images, etc.)
# -------------------------
MEDIA_URL = '/media/'

# Use Railway volume in production, local folder in development

# Local development: Use local media folder
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------------
# DEFAULT PRIMARY KEY TYPE
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
# LOGGING
# -------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}
