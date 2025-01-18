from django.db import models

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