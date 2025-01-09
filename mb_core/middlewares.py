from django.conf import settings
from .models import Tenant
from .util import make_db_connection

class TenantMiddleware:
    """
    Middleware to set the current tenant based on the request's subdomain or domain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        make_db_connection(settings.MASTER_DB_DSN)
        host = request.get_host()
        host_without_port = host.split(':')[0]  # Remove port if present

        # Normalize host by removing "www." if it exists
        if host_without_port.startswith('www.'):
            host_without_port = host_without_port[4:]
        
        parts = host_without_port.split('.')

        tenant = None

        # Check if the host is in the format of subdomain.domain.com
        if len(parts) > 3:  # Subdomain exists
            subdomain = parts[0]  # Extract subdomain (e.g., "john" in "john.mb.com")
            tenant = Tenant.objects.filter(slug=subdomain).using('master').first()
        else:
            # Skip tenant query and connection switch if the domain matches APP_DOMAIN
            if host_without_port == settings.APP_DOMAIN:
                return self.get_response(request)
            domain = host_without_port  # Extract domain (e.g., "john" in "john.com")
            tenant = Tenant.objects.filter(domain=domain).first()

        if tenant:
            make_db_connection(tenant.dsn)
            request.session['tenant_type'] = tenant.entity
            request.session['is_human_tenant'] = tenant.entity == 'human'
        else:
            request.session['tenant_type'] = None
            request.session['is_human_tenant'] = False

        return self.get_response(request)
