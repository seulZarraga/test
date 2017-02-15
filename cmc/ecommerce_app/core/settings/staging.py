"""
Django settings for carpool project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
# settings/base.py

from .base import *
import dj_database_url

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['stg.mexe-art.com']

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 1
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = False
X_FRAME_OPTIONS = 'DENY'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

DEFAULT_FILE_STORAGE = 'core.custom_storages.MediaS3BotoStorage'

MEDIA_ROOT = MEDIA_PATH



# Database settings

DATABASES['default'] = dj_database_url.config()

# Algolia settings

ALGOLIA = {
    'APPLICATION_ID': 'WJMK4HGJBF',
    'API_KEY': '587bd18cf37155b410903fa3e4e0734c',
    'SEARCH_KEY': '8ff28a1282bcafcbd392488a07e94a2c',
    'INDEX_PREFIX': 'staging',
}

