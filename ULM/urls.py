from django.urls import path
from .views import AuthenticationView, UserDetailView, TestView, create_superuser, SetAuthentication, UserEditView, PersonsListView, CreateUser, UpdateUser, ClearAuthentication
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('authentication/', AuthenticationView.as_view(), name='authentication_view'),
    path('set-authentication/', SetAuthentication.as_view(), name='SetAuthentication'),
    path('get-authentication/', SetAuthentication.as_view(), name='GetAuthentication'),
    path('clear-authentication/', ClearAuthentication.as_view(), name='ClearAuthentication'),

    path('authentication/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authentication/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('authentication/user/', UserDetailView.as_view(), name='user_detail_view'),
    path("create-superuser", create_superuser, name="create_superuser"),
    path('test/', TestView.as_view(), name='test'),
    path('person/<int:id>/edit', UserEditView.as_view(), name='edit-person'),
    path('persons/', PersonsListView.as_view(), name='persons'),
    path('create/', CreateUser.as_view(), name='create_user'),
    path('update/<int:id>', UpdateUser.as_view(), name='update_user'),
]
