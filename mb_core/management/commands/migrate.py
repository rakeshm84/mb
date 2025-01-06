from django.core.management.commands.migrate import Command as MigrateCommand
from django.conf import settings
from mb_core.models import Tenant
from django.db import connections
from django.db.utils import ConnectionDoesNotExist

class Command(MigrateCommand):
    help = "Run migrations for the master database first, then for all tenant databases in a multi-tenant setup"

    def handle(self, *args, **options):
        # Step 1: Run migrations for the master database
        master_db_name = settings.MASTER_DB_NAME
        self.stdout.write(f"Applying migrations for the master database: {master_db_name}")

        try:
            # Apply migrations on the master database
            super().handle(*args, **options)
        except Exception as e:
            self.stderr.write(f"Error migrating master database {master_db_name}: {e}")
            return

        self.stdout.write("Migrations completed for the master database.")

        # Step 2: Fetch all tenants from the master database
        try:
            tenants = Tenant.objects.all()
        except Exception as e:
            self.stderr.write(f"Error fetching tenants: {e}")
            return

        # Step 3: Run migrations for each tenant database
        for tenant in tenants:
            db_name = tenant.db_name
            self.stdout.write(f"Applying migrations for tenant: {tenant.name} (Database: {db_name})")

            # Dynamically update the database settings
            settings.DATABASES['default']['NAME'] = db_name

            # Ensure the database connection uses the updated settings
            try:
                connections['default'].close()  # Close any existing connection
                connections['default'].settings_dict.update({'NAME': db_name})
            except ConnectionDoesNotExist:
                self.stderr.write(f"Database connection for {db_name} does not exist.")
                continue

            # Apply migrations for the current tenant
            try:
                super().handle(*args, **options)
            except Exception as e:
                self.stderr.write(f"Error migrating tenant database {db_name}: {e}")

        self.stdout.write("Migrations completed for all tenant databases.")
