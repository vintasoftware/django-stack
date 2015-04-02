# Django stack

Some gidelines to configuring a new django project.
Currently meant for Django 1.7

## Dependencies

```
pip install python-decouple
pip install dj-database-url
pip install django-bower
pip install django-storages
pip install boto
pip install django-compressor
pip install Collectfast
pip install django-compressor

git+https://github.com/vintasoftware/django-naomi.git@fix-webbrowser-open#egg=django-naomi
```

## settings.py

```
import os

from decouple import config
from dj_database_url import parse as db_url


PRODUCTION = 'PRODUCTION_ENV' in os.environ

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def base_dir_join(*args):
    return os.path.join(BASE_DIR, *args)

DEBUG = config('DEBUG', default=True, cast=bool)
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = config('SECRET_KEY', default='123')

INSTALLED_APPS = (
	...
    'collectfast', # collectfast must come before staticfiles in Django 1.7+
    'django.contrib.staticfiles',
    ...
    'storages',
    'compressor',
    'djangobower',
    ...
)

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + base_dir_join('db.sqlite3'),
        # default='postgres://localhost:5432/myapp',
        cast=db_url)
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
    'compressor.finders.CompressorFinder',
)

# storages
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False
AWS_S3_CUSTOM_DOMAIN = '{0}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)

DEFAULT_FILE_STORAGE = config('DEFAULT_FILE_STORAGE',
    default='django.core.files.storage.FileSystemStorage')
STATICFILES_STORAGE = config('STATICFILES_STORAGE',
    default='django.contrib.staticfiles.storage.StaticFilesStorage')

STATIC_ROOT = base_dir_join('staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = base_dir_join('media')
MEDIA_URL = '/media/'

if PRODUCTION:
    STATIC_URL = 'http://{0}/static/'.format(AWS_S3_CUSTOM_DOMAIN)
    MEDIA_URL = 'http://{0}/media/'.format(AWS_S3_CUSTOM_DOMAIN)

# collectfast
AWS_PRELOAD_METADATA = True
COLLECTFAST_CACHE = 'collectfast'
COLLECTFAST_ENABLED = PRODUCTION

# bower
BOWER_COMPONENTS_ROOT = base_dir_join('components')

# compressor
COMPRESS_ENABLED = config('COMPRESS_ENABLED', default=False)
COMPRESS_STORAGE = STATICFILES_STORAGE
COMPRESS_URL = STATIC_URL

# email
if not PRODUCTION:
    INSTALLED_APPS += ('naomi',)
    EMAIL_BACKEND = 'naomi.mail.backends.naomi.NaomiBackend'
    EMAIL_FILE_PATH = base_dir_join('tmp_email')
else:
    SERVER_EMAIL = config('SERVER_EMAIL')
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT')
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

TEMPLATED_EMAIL_TEMPLATE_DIR = 'emails/'
TEMPLATED_EMAIL_FILE_EXTENSION = 'email'

# caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'collectfast': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_db_cache_collectfast',
        'TIMEOUT': 60 * 60 * 24 * 7 * 30,  # 1 month
        'OPTIONS': {
            'MAX_ENTRIES': 10000
        }
    }
}

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'segment': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

```

## package.json
```
{"private": true,"dependencies": {"bower": "*"}}
```

## .editorconfig

```
# editorconfig.org

root = true

[*]
indent_style = space
indent_size = 4
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.js]
indent_size = 2

[*.html]
indent_size = 2

[*.scss]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

# Makefile

```
clean:
    @find . -name "*.pyc" -delete
```

## Heroku

### Procfile

```
web: gunicorn myapp.wsgi --log-file -
```

### Builpack

```.buildpack```
```
https://github.com/heroku/heroku-buildpack-nodejs.git
https://github.com/vintasoftware/heroku-buildpack-python-with-django-bower.git
```

Commands to run on first deploy:
```
heroku config:set BUILDPACK_URL=https://github.com/vintasoftware/heroku-buildpack-multi.git
heroku run python manage.py createcachetable django_db_cache_collectfast
```
