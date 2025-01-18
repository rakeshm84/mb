from django.db import models
from django.contrib.auth.models import User

class Tenant(models.Model):
    parent_id = models.IntegerField(null=False, default=0)
    entity = models.CharField(max_length=100)
    entity_id = models.IntegerField(null=False, default=0)
    firstname = models.CharField(max_length=150, blank=True, null=True)
    lastname = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True, null=True)
    db_name = models.CharField(max_length=100, unique=True)
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

    class Meta:
        db_table = "user_profile"

    def __str__(self):
        return f"{self.user.username}'s Profile"