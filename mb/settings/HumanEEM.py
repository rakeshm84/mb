from .base import *

DEBUG = True

ENABLE_SERVICES = ['HumanEEM']

INSTALLED_APPS += [
    'HumanEEM',
]

MIDDLEWARE += [
    'HumanEEM.middleware.DatabaseMiddleware',
]


