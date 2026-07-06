from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
VNPAY_RETURN_URL = "https://navigate-backward-sage.ngrok-free.dev/api/wallet/topup/vnpay/result/"  # get from config
VNPAY_PAYMENT_URL = (
    "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"  # get from config
)
VNPAY_API_URL = "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction"
VNPAY_TMN_CODE = "VNPAY202"  # Website ID in VNPAY System, get from config
VNPAY_HASH_SECRET_KEY = (
    "9U0RE0VREK9L3K159B5O32UXR24X79OF"  # Secret key for create checksum,get from config
)

# Stripe configuration
STRIPE_PUBLISHABLE_KEY = "pk_test_51TkpnARuDgugaDReYpp9OI45GWrJ6Ceq8UGaJibhmHd9QZ00uNWgoPXXNfIA1iIjwCwX4UVzsbdWsGlq8k69VGaj00q9ueOXwm"
STRIPE_SECRET_KEY = "sk_test_51TkpnARuDgugaDRen1N64IetOEcfhioMyHcbIZfVHjmHbP64mhkriEApk1bMiBWn1RvCNlF43Z4KiZmWl5qBxT0Z00gRqfMhIe"
STRIPE_WEBHOOK_SECRET = "whsec_jeYVUSC8RMR865OWOiWmqSKTVF6UZWnU"  # Set this when you configure Stripe webhooks in the dashboard

SECRET_KEY = "django-insecure-th-%d0roim2x$t-+inu!(v_eav@635=c30k*-=igvm$-uq_8jy"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "apps.accounts",
    "apps.deck",
    "apps.note",
    "apps.card",
    "apps.payment",
    "infrastructure.payment",
    "drf_spectacular",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

# Đảm bảo Django cho phép dùng Session trong API
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "EXCEPTION_HANDLER": "core.exceptions.exception_handler.custom_exception_handler",
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,  # Cấp Refresh Token mới mỗi khi làm mới Access Token
    "BLACKLIST_AFTER_ROTATION": True,  # Vô hiệu hóa Token cũ sau khi đã xoay vòng
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Raki API",
    "DESCRIPTION": "API documentation for flashcard study app",
    "VERSION": "1.0.0",
    "COMPONENT_SPLIT_REQUEST": True,
}

# Email configuration (SMTP via Gmail)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "halequyen1725@gmail.com"
EMAIL_HOST_PASSWORD = "zuqo umap whyj yfgk"
DEFAULT_FROM_EMAIL = "Raki App <halequyen1725@gmail.com>"


REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0

# Mail Service
MAIL_SERVICE_URL = "http://mail-service:8000"
CHAT_SERVICE_URL = "http://chat-service:8000"
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "dev-secret-internal-token")
