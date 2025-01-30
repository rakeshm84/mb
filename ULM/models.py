from django.db import models
from django.contrib.auth.models import User, Group

class Entity(models.TextChoices):
    HUMAN = "human", "Human"
    BUSINESS = "business", "Business"

class Tenant(models.Model):
    parent_id = models.IntegerField(null=False, default=0)
    # entity = models.CharField(max_length=100)
    entity = models.CharField(
        max_length=50,
        choices=Entity.choices,
        default=None,
        null=True,
        blank=True
    )
    entity_id = models.IntegerField(null=False, default=0)
    firstname = models.CharField(max_length=150, blank=True, null=True)
    lastname = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True, null=True)
    db_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    dsn = models.TextField(null=True)
    status = models.BooleanField(default=True, null=False)
    shared_id = models.IntegerField(null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    updated_at = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "user_profile"

    def __str__(self):
        return f"{self.user.username}'s Profile"

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class PermissionsMeta(models.Model):
    id = models.AutoField(primary_key=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    model_id = models.PositiveIntegerField()
    tenant_id = models.IntegerField()
    parent_tenant_id = models.IntegerField()

    # Generic Foreign Key
    content_object = GenericForeignKey('content_type', 'model_id')

    class Meta:
        db_table = "permissions_meta"

    def __str__(self):
        return f"{self.content_type} - {self.model_id} (Tenant: {self.tenant_id})"
    

def custom_has_permission(self, perm):
    if self.is_tenant:
        return perm in self.permissions
    
def is_admin_user(self):
    is_admin = False
    if hasattr(self, 'is_admin'):
        is_admin = self.is_admin
    elif hasattr(self, 'tenant_id'):
        tenant_user = TenantUser.objects.get(user_id=self.id, tenant_id=self.tenant_id)
        if tenant_user:
            is_admin = tenant_user.is_admin
    
    if hasattr(self, 'is_superuser') and self.is_superuser:
        is_admin = True
    return is_admin


User.add_to_class('has_permission', custom_has_permission)
User.add_to_class('is_admin_user', is_admin_user)

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"

    def __str__(self):
        return f"{self.name} - {self.description} (Price: {self.price})"
    
class Entity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "entities"

class EntityContentType(models.Model):
    id = models.AutoField(primary_key=True)
    entity_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    class Meta:
        db_table = "entity_content_type"

class TenantUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_users')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='tenant_users')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tenant_users')
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False, null=False)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenant_users')

    class Meta:
        db_table = 'tenant_users'
        unique_together = ('user', 'tenant')  # Ensures no duplicate user-tenant entries.

    def __str__(self):
        return f"{self.user.username} - {self.tenant.name}"