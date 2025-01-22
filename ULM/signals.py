from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import PermissionsMeta, Tenant
from threading import local


# Thread-local storage to hold tenant ID
_thread_locals = local()

def set_tenant(tenant_id, parent_tenant_id):
    _thread_locals.tenant_id = tenant_id
    _thread_locals.parent_tenant_id = parent_tenant_id

def get_current_tenant():
    return getattr(_thread_locals, 'tenant_id', None)

def get_parent_tenant():
    return getattr(_thread_locals, 'parent_tenant_id', None)

##############################################################################################

# Utility function to create a PermissionsMeta record
def create_permission_meta(content_type_model, model_id):
    tenant_id = get_current_tenant() or 0
    parent_tenant_id = get_parent_tenant() or 0
    content_type = ContentType.objects.get_for_model(content_type_model)
    PermissionsMeta.objects.create(
        content_type=content_type,
        model_id=model_id,
        tenant_id=tenant_id,
        parent_tenant_id=parent_tenant_id
    )

# Signal for User model
@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:  # Only for newly created records
        if instance.is_superuser == 1:
            group, created = Group.objects.get_or_create(name="human_admin")
            permissions = Permission.objects.filter(codename__in=['view_tenant', 'view_userprofile'])
            group.permissions.set(permissions)
        # create_permission_meta(User, instance.id)

# Signal for Group model
@receiver(post_save, sender=Group)
def group_post_save(sender, instance, created, **kwargs):
    if created:
        create_permission_meta(Group, instance.id)

# Signal for Permission model
@receiver(post_save, sender=Permission)
def permission_post_save(sender, instance, created, **kwargs):
    if created:
        create_permission_meta(Permission, instance.id)

# Signal for User-Group relationships (through table: auth_user_groups)
@receiver(m2m_changed, sender=User.groups.through)
def user_groups_m2m_changed(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":  # After adding a new relation
        for group_id in pk_set:
            create_permission_meta(Group, group_id)

# Signal for User-Permission relationships (through table: auth_user_user_permissions)
@receiver(m2m_changed, sender=User.user_permissions.through)
def user_permissions_m2m_changed(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for permission_id in pk_set:
            create_permission_meta(Permission, permission_id)

##############################################################################################

# Utility function to create a Group record
def create_new_group_for_tenant_user(tenant):
    group, created = Group.objects.get_or_create(name=f"{tenant.entity}_admin")
    # permission = Permission.objects.get(codename='view_tenant')
    # group.permissions.add(permission)
    user = User.objects.get(id=tenant.entity_id)
    user.groups.add(group)

# Signal for Tenant model
@receiver(post_save, sender=Tenant)
def tenant_post_save(sender, instance, created, **kwargs):
    if created:
        set_tenant(instance.id, instance.parent_id)
        create_new_group_for_tenant_user(instance)
        set_tenant(None, None)
