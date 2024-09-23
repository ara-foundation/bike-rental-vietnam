"""
Django settings for cb_portal project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['bike-rental-78eb34f96e21.herokuapp.com']
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bike_rental",
    "debug_toolbar",
    "tours.apps.TourConfig",
    "rest_framework",
    "api",
    "import_export",
    "django_extensions",
    "django_filters",
    "widget_tweaks",
    "storages",
    'compressor',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = "cb_portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cb_portal.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "bike_rental/static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',  'compressor.filters.cssmin.CSSMinFilter']

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = config("AWS_S3_ENDPOINT_URL") + "/media/"
# MEDIA_ROOT = BASE_DIR / "media"

THEME_COLOR = "sandstone"
CUSTOM_CSS = "css/bikes.css"

# Use django-storages to manage static and media files with R2
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = config("R2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("R2_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("R2_BUCKET_NAME")

# Cloudflare R2 uses custom endpoints, so you need to specify it
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")

# You can set these optional configurations to enhance the performance and security
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

AWS_LOCATION = "media/"  # If you want to separate media files from others
AWS_DEFAULT_ACL = None  # To avoid issues with ACLs, set to None
AWS_QUERYSTRING_AUTH = False  # Disable querystring authentication for public files
