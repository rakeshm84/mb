from .base import *

DEBUG = True

ENABLE_SERVICES = ['HumanEEM'];
INSTALLED_APPS += [
    'HumanEEM',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'app1_db',
        'USER': 'app1_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
