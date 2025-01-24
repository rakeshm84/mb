from django.urls import path
from .views import TestView, CreateHuman, RolesListView, PermissionListView, GroupCreateView

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('create/', CreateHuman.as_view(), name='create_human'),
    path('get_roles/', RolesListView.as_view(), name='roles_list'),
    path('get-all-permissions/', PermissionListView.as_view(), name='get-all-permissions/'),
    path("create_group/", GroupCreateView.as_view(), name="create_group"),
]