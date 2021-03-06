"""
Django settings for ecommerce_app project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import getpass

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8lu*6g0lg)9z!ba+a$ehk)xt)x%rxgb$i1&amp;022shmi1jcgihb*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = INSTALLED_APPS + [
    'django_extensions',
    'debug_toolbar',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_compressed')
MEDIA_ROOT = MEDIA_PATH


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ALGOLIA = {
    'APPLICATION_ID': 'CIOFIUHQVQ',
    'API_KEY': '0a64dadab47281bc86f846551a9e4284',
    'INDEX_PREFIX': 'local_' + getpass.getuser(),
    'SEARCH_KEY': '6d2b7726c13f6a39a64f576047edae70',
}
