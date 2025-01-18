from .base import *

DEBUG = True
ENABLE_SERVICES = ['ULM'];
INSTALLED_APPS += [
    'ULM',
]
STATIC_URL = 'static/'

# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'react', 'build', 'static')]

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'ULM','react', 'build', 'static')]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'ULM/react/build'], 
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
