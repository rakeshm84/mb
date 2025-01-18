from django.urls import path
from .views import TestView, CreateHuman

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('create/', CreateHuman.as_view(), name='create_human'),
]