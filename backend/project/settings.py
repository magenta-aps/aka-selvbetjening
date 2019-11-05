"""
Django settings for aka project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
SITE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SITE_DIR)
PROJECT_DIR = os.path.dirname(BASE_DIR)
SHARED_DIR = os.path.join(PROJECT_DIR, "shared")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

MEDIA_URL = BASE_DIR + '/upload/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {  # A flag to only log specified in production
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {  # A flag used for DEBUGGING only logs
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{name} {levelname} {asctime} {module} {funcName} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'debug-console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'aka': {
            'handlers': ['debug-console'],
            'filters': ['require_debug_true'],
            'level': 'DEBUG'
        },
        'oic': {
            'handlers': ['debug-console'],
            'filters': ['require_debug_true'],
            'level': 'DEBUG'
        }
    }
}

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'aka',
    'openid'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'openid.middleware.openid.LoggedIn',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'frontend', 'dist')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'da-dk'
TIME_ZONE = 'America/Godthab'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [ os.path.join(BASE_DIR, 'i18n') ]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATICFILES_DIRS = [os.path.join(PROJECT_DIR, 'frontend', 'dist', 'static'), os.path.join(PROJECT_DIR, 'frontend', 'dist')]

SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # expire session on browser close

PRISME_CONNECT = {
    'wsdl_file': 'https://test.erp.gl/GWCServiceSetup/GenericService.svc?singleWsdl',
    'proxy': {
        'socks': ''
    },
    'auth': {
        'basic': {
            'username': '',
            'domain': '',
            'password': ''
        }
    }
}

DAFO_CONNECT = {
    'address': {
        'token': 'https://sts.data.gl/get_token_passive?username={username}&password={password}',
        'cvr': 'https://data.gl/prisme/cvr/1/{cvr}'
    },
    'auth': {
        'username': '',
        'password': ''
    }
}
OPENID_CONNECT = {}

# Max 2 MB - can be lower if we want
MAX_UPLOAD_FILESIZE = 22097152

LOCAL_SETTINGS_FILE = os.path.join(SITE_DIR, "local_settings.py")
if os.path.exists(LOCAL_SETTINGS_FILE):
    from .local_settings import *  # noqa

SECRET_KEY_FILE = os.path.join(SITE_DIR, "secret_key.py")
if os.path.exists(SECRET_KEY_FILE):
    from .secret_key import *  # noqa
