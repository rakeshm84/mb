from django.urls import path
from .views import TestView, Create, PersonsView, RecentRegistrationView, RolesListView, PermissionListView, GroupCreateView, GroupUpdateView, FetchRoleView, SetLanguageView, PersonsEditView, EditProfile, UsersListView, UserCreateView, UserEditView, UserUpdateView, BindExistingUser
from rest_framework_simplejwt.views import  TokenVerifyView


urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('create/', Create.as_view(), name='create'),
    path('persons/', PersonsView.as_view(), name='persons'),
    path('person/<int:id>/edit/', PersonsEditView.as_view(), name='update-person'),
    path('recent_registration/', RecentRegistrationView.as_view(), name='recent_registration'),
    path('get_roles/', RolesListView.as_view(), name='roles_list'),
    path('get-all-permissions/', PermissionListView.as_view(), name='get-all-permissions/'),
    path("create_group/", GroupCreateView.as_view(), name="create_group"),
    path("update_group/<int:id>/edit/", GroupUpdateView.as_view(), name="create_group"),
    path('get_role/<int:id>/', FetchRoleView.as_view(), name='edit-person'),
    path('set-language/', SetLanguageView.as_view(), name='set-language'),
    path('profile/<int:id>/edit/', EditProfile.as_view(), name='edit_profile'),
    
    path('get_users/', UsersListView.as_view(), name='users_list'),
    path('create_user/', UserCreateView.as_view(), name='create_user'),
    path('user/<int:id>/edit/', UserEditView.as_view(), name='edit_user'),
    path('update_user/<int:id>/', UserUpdateView.as_view(), name='update_user'),
    path('bind_user/', BindExistingUser.as_view(), name='bind_user'),
]