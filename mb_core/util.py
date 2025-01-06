from urllib.parse import urlparse
from django.db import connection

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

def make_db_connection(dsn):
    db_settings = parse_connection_string(dsn)
    if db_settings:
        connection.close()
        connection.settings_dict.update(db_settings)
        connection.connect()