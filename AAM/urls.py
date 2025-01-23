from django.urls import path
from .views import TestView, Create, PersonsView, RecentRegistrationView, RolesListView, PermissionListView, GroupCreateView
from rest_framework_simplejwt.views import  TokenVerifyView


urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('create/', Create.as_view(), name='create'),
    path('persons/', PersonsView.as_view(), name='persons'),
    path('recent_registration/', RecentRegistrationView.as_view(), name='recent_registration'),
    path('get_roles/', RolesListView.as_view(), name='roles_list'),
    path('get-all-permissions/', PermissionListView.as_view(), name='get-all-permissions/'),
    path("create_group/", GroupCreateView.as_view(), name="create_group"),
]