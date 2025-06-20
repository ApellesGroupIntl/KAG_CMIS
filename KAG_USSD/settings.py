"""
Django settings for KAG_USSD project.

Generated by 'django-admin startproject' using Django 5.0.12.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+tm6qt&07eil&lvoolvt@le5awj$+2vs+%-27c$)*v#7t1bc8q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [ "33f0-217-199-148-234.ngrok-free.app", "*",'*', "127.0.0.1",
    "localhost"]

CSRF_TRUSTED_ORIGINS = [
    "https://33f0-217-199-148-234.ngrok-free.app"
]


# Application definition

INSTALLED_APPS = [
    #'Users'
    'Local_Church',
    'Section',
    'District',
    'USSD_CORE',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'KAG_USSD.urls'

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

WSGI_APPLICATION = 'KAG_USSD.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_new.sqlite3',
    },
'secondary': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'backup_db.sqlite3',
},
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JAZZMIN_SETTINGS = {
    "show_ui_builder": False,  # Hide UI builder (optional)
    "show_version": False,     # Hide the Jazzmin version at the bottom
    "app_list": {},
    # Copyright on the footer
    "search_model": ["auth.User", "auth.Group"],

    "site_title": "KAG MURANGÁ Portal",
    "site_header": "KAG MURANGÁ Portal",
    "site_brand": "KAG MURANGÁ Portal",
    "welcome_sign": "Welcome to the KAG MURANGÁ Portal Admin",
    "copyright": "KAG MURANGÁ & Powered by Apelles Group Intl",

    # Optional customizations
    "site_logo": "images/kag.png",  # Add your logo if needed
    "login_logo": "images/kag.png",
    "show_sidebar": True,
    "navigation_expanded": True,
    "custom_css": "css/jazzmin_override.css",

}


STATICFILES_DIRS = [
    BASE_DIR / "static",  # If you're using a global static folder
]

STATIC_ROOT = BASE_DIR / "staticfiles"  # Needed if running collectstatic #python manage.py collectstatic --running during production
CSRF_TRUSTED_ORIGINS = [
    "https://55e0-41-139-219-203.ngrok-free.app",
]

#DATABASE_ROUTERS = ['Local_Church.routers.DatabaseRouter']

#AUTH_USER_MODEL = 'Users.CustomUser'

