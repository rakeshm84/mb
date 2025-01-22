from django.db import connection
from django.db.utils import ProgrammingError
from django.conf import settings
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from django.core.management import call_command
from urllib.parse import urlparse
from django.db import connection

def connect_db(database_name):
    """
    Switch the database connection to the tenant's database.
    """
    connection.settings_dict['NAME'] = database_name 
    connection.connect() 

def create_db(db_name):
    """
    Create the database, run migrations, and create necessary tables.
    """

    target_database = None
    try:       
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"CREATE DATABASE {db_name};")
                target_database = db_name
            except:
                return
    except ProgrammingError as e:
        return None
    
    if not target_database:
        return None
    
    return target_database

def run_migrations(database):
    """
    Manually create and apply pending migrations for the specified database.
    """
    try:
        connect_db(database)
    except Exception as e:
        return False, f"Error making db connection: {e}"

    # Ensure the migration table exists
    MigrationRecorder(connection).ensure_schema()

    # Run the migrations
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()  # Get all migration targets

    try:
        # Apply all migrations
        executor.migrate(targets)
        return True, "Migrations applied successfully."
    except Exception as e:
        return False, f"Error applying migrations: {e}"

def parse_connection_string(connection_string):
    parsed = urlparse(connection_string)
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': parsed.path.lstrip('/'),
        'USER': parsed.username,
        'PASSWORD': parsed.password or '',
        'HOST': parsed.hostname,
        'PORT': parsed.port or '',
    }

def make_db_connection(dsn):
    db_settings = parse_connection_string(dsn)
    if db_settings:
        connection.close()
        connection.settings_dict.update(db_settings)
        connection.connect()