from .base import *

DEBUG = True
ENABLE_SERVICES = ['AAM'];
INSTALLED_APPS += [
    'AAM'
]
STATIC_URL = 'static/'

# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'react', 'build', 'static')]

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'AAM','react', 'build', 'static')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('ADMIN_DB_NAME'),
        'USER': env('ADMIN_DB_USER'),
        'PASSWORD': env('ADMIN_DB_PASSWORD'),
        'HOST': env('ADMIN_DB_HOST'),
        'PORT': env('ADMIN_DB_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",  # Optional for strict SQL mode
            'charset': 'utf8',
        },
    },
    'master': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('ADMIN_DB_NAME'),
        'USER': env('ADMIN_DB_USER'),
        'PASSWORD': env('ADMIN_DB_PASSWORD'),
        'HOST': env('ADMIN_DB_HOST'),
        'PORT': env('ADMIN_DB_PORT'),                 # Default MySQL port
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",  # Optional for strict SQL mode
            'charset': 'utf8',
        },
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'AAM/react/build'], 
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
