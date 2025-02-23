"""
URL configuration for mb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import AuthenticationView, UserDetailView, TestView, Test2View, create_superuser
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('authentication/', AuthenticationView.as_view(), name='authentication_view'),
    path('authentication/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authentication/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('authentication/user/', UserDetailView.as_view(), name='user_detail_view'),
    path('fetch/<str:app_name>/<str:table_name>/<str:field>/<str:value>/', TestView.as_view(), name='fetch_record'),
    path('query', Test2View.as_view(), name='run_query'),
    path("create-superuser", create_superuser, name="create_superuser"),
]
