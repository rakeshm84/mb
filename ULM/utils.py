from django.db import connection
from django.db.utils import ProgrammingError
from django.conf import settings
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from urllib.parse import urlparse

def create_admin_db(user_id):
    """
    Create the admin database, run migrations, and create necessary tables.
    """
    source_database = settings.MASTER_DB_NAME
    db_name = source_database + "_admin_" + str(user_id)

   
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
    
    connect_db(target_database)
    # update_tenant_details(target_database)
    create_tables_for_admin(source_database,target_database)
    # admin_db_seeding(source_database, target_database)

    connect_db(source_database)

    return target_database

def list_all_tables(database_name):
    """
    Lists all tables in the specified tenant's database.
    """
    try:       
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")           
            tables = cursor.fetchall()           
            return [table[0] for table in tables] 
    
    except Exception as e:
        print(f"Error listing tables for {database_name}: {e}")
        return []
    
def connect_db(database_name):
    """
    Switch the database connection to the tenant's database.
    """
    connection.settings_dict['NAME'] = database_name 
    connection.connect() 

def create_tables_for_admin(source_database, target_database):
    """
    Create the tables for the tenant database.
    """
    
    try:
        
        all_tables = list_all_tables(source_database)
        admin_tables = get_admin_manager_tables()
        run_migrations()
 
        # for table_name in admin_tables:
        #     with connection.cursor() as cursor:  
        #         cursor.execute(f"""
        #         CREATE TABLE IF NOT EXISTS {target_database}.{table_name} 
        #         LIKE {source_database}.{table_name};
        #         """)
    except Exception as e:
        return None

def get_admin_manager_tables():
    return ['django_content_type', 'django_migrations', 'django_sessions', 'tenants', 'user_profile']

def admin_db_seeding(masterDB, tenantDB):
    seeding_tables = get_default_seed_tables_for_admin()

    for table_name in seeding_tables:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO {tenantDB}.{table_name} 
                SELECT * FROM {masterDB}.{table_name};
            """)

def get_default_seed_tables_for_admin():
    return ['django_content_type', 'django_migrations']

def run_migrations(database='default'):
    """
    Manually apply pending migrations for the specified database.
    """
    connection = connections[database]

    # Ensure the migration table exists
    MigrationRecorder(connection).ensure_schema()

    # Run the migrations
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()  # Get all migration targets

    try:
        # Apply all migrations
        executor.migrate(targets)
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Error applying migrations: {e}")

def parse_connection_string(connection_string):
    parsed = urlparse(connection_string)
    return {
        'ENGINE': 'django.db.backends.mysql',  # Adjust based on your database type
        'NAME': parsed.path.lstrip('/'),
        'USER': parsed.username,
        'PASSWORD': parsed.password or '',
        'HOST': parsed.hostname,
        'PORT': parsed.port or '',
    }

def _dsn_to_string(dsn, with_auth=True):
    """
    Function to convert a dictionary containing database connection details into a DSN string.
    
    :param dsn: Dictionary containing database connection details (driver, host, dbname, user, password).
    :param with_auth: Boolean flag to include authentication details in the DSN string.
    :return: DSN string representing the database connection.
    """

    # Extract individual components from the DSN dictionary
    driver = dsn.get('driver', settings.DATABASES['default']['ENGINE'].split('.')[-1])
    host = dsn.get('host', settings.DATABASES['default']['HOST'])
    dbname = dsn.get('dbname', settings.DATABASES['default']['NAME'])
    user = dsn.get('user', settings.DATABASES['default']['USER'])
    password = dsn.get('password', settings.DATABASES['default']['PASSWORD'])
    port = dsn.get('port', settings.DATABASES['default']['PORT'])

    # Build the basic DSN string
    dsn_string = f"{driver}://{host}:{port}/{dbname}"

    # If 'with_auth' is false, return the basic DSN string without authentication details
    if not with_auth:
        return dsn_string

    # Append authentication details to the DSN string
    dsn_string = f"{driver}://{user}:{password}@{host}:{port}/{dbname}"

    return dsn_string