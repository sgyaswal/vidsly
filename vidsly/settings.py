"""
Django settings for vidsly project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
# SECRET_KEY = config('AWS_ACCESS_KEY_ID')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import os

####################### INITIALISE #######################
envs = os.environ

LOG_DELETION=envs.get('LOG_DELETION_DAY', 15)
# HOST=envs.get("HOST_SERVER_URL",'http://localhost:8000')
# DJANGO_DATABASE_NAME= envs.get('DJANGO_DATABASE_NAME', '')
# DJANGO_DATABASE_USER=  envs.get('DJANGO_DATABASE_USER', '')
# DJANGO_DATABASE_PASSWORD= envs.get('DJANGO_DATABASE_PASSWORD', '')
# DJANGO_DATABASE_SERVER=  envs.get('DJANGO_DATABASE_SERVER', '')


# AWS_SES_REGION_NAME = envs.get('AWS_SES_REGION_NAME','')
# AWS_ACCESS_KEY_ID = envs.get('AWS_ACCESS_KEY_ID','')
# AWS_SECRET_ACCESS_KEY= envs.get('AWS_SECRET_ACCESS_KEY','')
# AWS_SES_VERIFY_EMAIL=envs.get('AWS_SES_VERIFY_EMAIL','')
# AWS_STORAGE_BUCKET_NAME = envs.get('AWS_STORAGE_BUCKET_NAME','')
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = True


HOST=config("HOST_SERVER_URL",'http://localhost:8000')
DJANGO_DATABASE_NAME= config('DJANGO_DATABASE_NAME', '')
DJANGO_DATABASE_USER=  config('DJANGO_DATABASE_USER', '')
DJANGO_DATABASE_PASSWORD= config('DJANGO_DATABASE_PASSWORD', '')
DJANGO_DATABASE_SERVER=  config('DJANGO_DATABASE_SERVER', '')


AWS_SES_REGION_NAME = config('AWS_SES_REGION_NAME','')
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID','')
AWS_SECRET_ACCESS_KEY= config('AWS_SECRET_ACCESS_KEY','')
AWS_SES_VERIFY_EMAIL=config('AWS_SES_VERIFY_EMAIL','')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME','')

print(AWS_ACCESS_KEY_ID)



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-h9pw0u=0)8x&o=g*kjwsux!d_n1tlh-ye=yc2^%&e@#77gyu)u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3030',
# ] # If this is used, then not need to use `CORS_ALLOW_ALL_ORIGINS = True`
CORS_ALLOWED_ORIGIN_REGEXES = [
    'http://localhost:5000',
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    "Authorization",
    "userName", 
    "password",
    'access-control-allow-origin',
    'authorization',
    'content-type',
]




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'user',
    'drf_yasg',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),

}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vidsly.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vidsly.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# myproject/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DJANGO_DATABASE_NAME,
        'USER': DJANGO_DATABASE_USER,
        'PASSWORD': DJANGO_DATABASE_PASSWORD,
        'HOST': DJANGO_DATABASE_SERVER,
        'PORT': '3306',
        'OPTIONS': {
            'host': DJANGO_DATABASE_SERVER,
        },
    }
}




from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=120),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            "description": "JWT authorization"
        }, 'basic': {
            'type': 'basic'
        }
    },
    'JSON_EDITOR': True,
    'TAGS_SORTER':'alpha',
    # 'FILTER':'tags'
    'MAX_DISPLAYED_TAGS':1
}



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MY_PROTOCOL = "http"
if HOST.count("https:")>0:
    MY_PROTOCOL = "https"
