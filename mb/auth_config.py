from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CustomAuthConfig(AppConfig):
    # Match the original app's name
    name = 'django.contrib.auth'

    # Optional: Set the verbose name
    verbose_name = "Authentication and Authorization"

    def ready(self):
        super().ready()
        # Disconnect the default permissions creation signal
        post_migrate.disconnect(
            dispatch_uid="django.contrib.auth.management.create_permissions"
        )
