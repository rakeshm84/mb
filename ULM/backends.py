from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission, Group
from .models import PermissionsMeta, TenantUser

class CustomPermissionBackend(ModelBackend):
    
    def get_all_permissions(self, user_obj, tenant_id=None):
        return get_tenant_permissions(user_obj, tenant_id)

    def get_user_permissions(self, user_obj, tenant_id=None):
        return get_tenant_user_permissions(user_obj, tenant_id)

    def get_group_permissions(self, user_obj, tenant_id=None):
        return get_tenant_group_permissions(user_obj, tenant_id)
    
    def has_perm(self, user_obj, perm, tenant_id=None):
        return perm in self.get_all_permissions(user_obj, tenant_id=tenant_id)
    
def get_tenant_permissions(user, tenant_id):
    """
    Fetch tenant-specific permissions for the given user and tenant ID.
    """

    user_permissions = get_tenant_user_permissions(user, tenant_id)

    group_permissions = get_tenant_group_permissions(user, tenant_id)

    # Combine user and group permissions
    all_permissions = user_permissions.union(group_permissions)

    return all_permissions

def get_tenant_user_permissions(user, tenant_id):
    """
    Fetch tenant-specific user permissions for the given user and tenant ID.
    """
    
    permission_ids = PermissionsMeta.objects.filter(
        tenant_id=0 if tenant_id == None else tenant_id,
        content_type__model='permission'
    ).values_list('model_id', flat=True)

    if not permission_ids:
        permission_ids = []

    user_permissions = Permission.objects.filter(id__in=permission_ids, user=user)

    return {f"{perm.content_type.model}.{perm.codename}" for perm in user_permissions}

# def get_tenant_group_permissions(user, tenant_id):
#     """
#     Fetch tenant-specific group permissions for the given user and tenant ID.
#     """
#     # Fetch groups created by the current tenant
#     group_ids = PermissionsMeta.objects.filter(
#         tenant_id=tenant_id,
#         content_type__model='group'
#     ).values_list('model_id', flat=True)

#     if not group_ids:
#         group_ids = []

#     # Use these group IDs to filter permissions
#     group_permissions = Permission.objects.filter(
#         group__id__in=group_ids,
#         group__user=user
#     )

#     return {f"{perm.content_type.model}.{perm.codename}" for perm in group_permissions}

def get_tenant_group_permissions(user, tenant_id):
    """
    Fetch tenant-specific group permissions for the given user and tenant ID.
    """

    # Get the user's group ID from the TenantUser table
    user_group_ids = TenantUser.objects.filter(user=user, tenant_id=tenant_id).values_list('group_id', flat=True)

    if not user_group_ids:
        return set()  # Return empty set if no groups found

    # Fetch groups created by the current tenant
    tenant_group_ids = PermissionsMeta.objects.filter(
        tenant_id=0 if tenant_id == None else tenant_id,
        content_type__model='group'
    ).values_list('model_id', flat=True)

    if not tenant_group_ids:
        return set()  # Return empty set if no tenant groups found

    # Filter only groups that belong to the user and the tenant
    valid_group_ids = set(user_group_ids).intersection(set(tenant_group_ids))

    if not valid_group_ids:
        return set()  # Return empty set if no valid groups

    # Use these group IDs to filter permissions
    group_permissions = Permission.objects.filter(group__id__in=valid_group_ids)

    return {f"{perm.content_type.model}.{perm.codename}" for perm in group_permissions}