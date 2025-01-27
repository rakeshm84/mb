from django.urls import path
from .views import AuthenticationView, UserDetailView, TestView, create_superuser, SetAuthentication, UserEditView, PersonsListView, CreateUser, UpdateUser, ClearAuthentication, RecentRegistrationView, CheckPermission, CreateCustomPermission, RolesListView, PermissionListView, GroupCreateView, CreateEntityAndAssignTable, UsersListView, CreateTenantUser, GroupUpdateView, FetchRoleView, TestFunc, SetLanguageView, UpdateTenantUser
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('authentication/', AuthenticationView.as_view(), name='authentication_view'),
    path('set-authentication/', SetAuthentication.as_view(), name='SetAuthentication'),
    path('get-authentication/', SetAuthentication.as_view(), name='GetAuthentication'),
    path('clear-authentication/', ClearAuthentication.as_view(), name='ClearAuthentication'),

    path('authentication/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authentication/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('authentication/user/', UserDetailView.as_view(), name='user_detail_view'),
    path('authentication/check/<str:type>', CheckPermission.as_view(), name='check'),
    path("create-superuser", create_superuser, name="create_superuser"),
    path('test/', TestView.as_view(), name='test'),
    path('person/<int:id>/edit/', UserEditView.as_view(), name='edit-person'),
    path('persons/', PersonsListView.as_view(), name='persons'),
    path('create/', CreateUser.as_view(), name='create_user'),
    path('update/<int:id>', UpdateUser.as_view(), name='update_user'),
    path('recent_registration/', RecentRegistrationView.as_view(), name='recent_registration'),
    path('create-permission/', CreateCustomPermission.as_view(), name='create_permission'),
    path('get_roles/', RolesListView.as_view(), name='roles_list'),
    path('get-all-permissions/', PermissionListView.as_view(), name='get-all-permissions'),
    path("create_group/", GroupCreateView.as_view(), name="create_group"),
    path('create-entity/', CreateEntityAndAssignTable.as_view(), name='create_entity'),
    path('get_users/', UsersListView.as_view(), name='users_list'),
    path('create-tenant-user/', CreateTenantUser.as_view(), name='create_users'),
    path('user/<int:id>/edit/', UpdateTenantUser.as_view(), name='update_tenant_user'),
    path("update_group/<int:id>/edit/", GroupUpdateView.as_view(), name="create_group"),
    path('get_role/<int:id>/', FetchRoleView.as_view(), name='edit-person'),
    path('test2/', TestFunc.as_view(), name='test2'),
    path('set-language/', SetLanguageView.as_view(), name='set-language'),  
]
