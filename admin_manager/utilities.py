from django.db import connection
from django.db.utils import ProgrammingError
from django.contrib.sessions.models import Session
from django.conf import settings
from mb_core.models import Tenant
from .serializers import TenantSerializer, UserSerializer

def connect_db(database_name):
    """
    Switch the database connection to the tenant's database.
    """
    connection.settings_dict['NAME'] = database_name 
    connection.connect() 

def create_tenant_database(tenant_dbname):
    """
    Creates a new tenant database for the tenant.
    """
    try:       
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"CREATE DATABASE {tenant_dbname};")
                print(f"Database {tenant_dbname} created.")
                return tenant_dbname
            except:
                print(f"Database {tenant_dbname} already exists.")
                return None
         
    except ProgrammingError as e:
        print(f"Error creating database {tenant_dbname}: {e}")
        return None

def get_current_tenant():
    session = Session.objects.get(session_key='tenant')
    session_data = session.get_decoded()
    if session_data:
        return session_data
    else:
        return None

def get_tenant_from_obj(obj):
    return obj

def set_current_tenant(request, tenant):
    request.session['tenant'] = tenant

def create_tenant_db(tenant_id):
    """
    Create the tenant database, run migrations, and create necessary tables.
    """
    source_database = settings.MASTER_DB_NAME
    table_names = list_all_tables(source_database)
    tenant_db_name = _get_db_name(tenant_id)

    return tenant_db_name;
    
    target_database = create_tenant_database(tenant_db_name)
    
    if not target_database:
        return
    
    
    connect_db(target_database)
    # update_tenant_details(target_database)
    create_tables_for_tenant(source_database,target_database, table_names)
    tenant_db_seeding(source_database, target_database)

    connect_db(source_database) 

    _setup_tenant_admin(tenant_id, target_database)
    

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
    
def create_tables_for_tenant(source_database, target_database, table_names):
    """
    Create the tables for the tenant database.
    """
    
    try:

        admin_tables = get_admin_manager_tables()
 
        for table_name in table_names:
            # if table_name in admin_tables:
            #     continue
            with connection.cursor() as cursor:  
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {target_database}.{table_name} 
                LIKE {source_database}.{table_name};
                """)    
                print(f"Table '{table_name}' created in {target_database}.")
            

    
    except Exception as e:
        print(f"Error creating tables for {target_database}: {e}")

def tenant_db_seeding(masterDB, tenantDB):
    seeding_tables = get_default_seed_tables()

    for table_name in seeding_tables:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO {tenantDB}.{table_name} 
                SELECT * FROM {masterDB}.{table_name};
            """)

def get_default_seed_tables():
    return ['auth_permission', 'django_content_type', 'django_migrations']

def get_admin_manager_tables():
    return ['admin_manager_person', 'admin_manager_tenant']

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

def update_tenant_details(dbname):
    pass
    dsn = {'dbname': dbname}
    update_data = {'dsn': _dsn_to_string(dsn), 'db_name': dbname}
    tenant_serializer_update = TenantSerializer(data=update_data, partial=True)  # `partial=True` allows partial updates
    if tenant_serializer_update.is_valid():
        tenant_serializer_update.save()

def _get_db_name(tenant_id):
    source_database = settings.MASTER_DB_NAME
    tenant = Tenant.objects.get(id=tenant_id)
    return tenant.db_name
    # tenant_db_name = source_database + '_tenant_' + data.entity + '_' + str(data.slug)
    # return tenant_db_name

def _setup_tenant_admin(tenant_id, tenant_db):
    tenant = Tenant.objects.get(id=tenant_id)
    if tenant:
        from django.contrib.auth.models import User
        auth_user_id = tenant.entity_id
        user_data = User.objects.get(id=auth_user_id)
        if user_data:
            connect_db(tenant_db)
            tenant_admin_data = User()
            tenant_admin_data.password = user_data.password
            tenant_admin_data.username = user_data.username
            tenant_admin_data.first_name = user_data.first_name
            tenant_admin_data.last_name = user_data.last_name
            tenant_admin_data.email = user_data.email
            tenant_admin_data.is_active = 1
            tenant_admin_data.is_superuser = 1
            tenant_admin_data.is_staff = 1
            tenant_admin_data.save()
            
            connect_db(settings.MASTER_DB_NAME) 
