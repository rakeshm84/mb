from django.urls import path
from .views import AuthenticationView, UserDetailView, TestView, create_superuser
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('authentication/', AuthenticationView.as_view(), name='authentication_view'),
    path('authentication/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authentication/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('authentication/user/', UserDetailView.as_view(), name='user_detail_view'),
    path("create-superuser", create_superuser, name="create_superuser"),
    path('test/', TestView.as_view(), name='test'),
]
