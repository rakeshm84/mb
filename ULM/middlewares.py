from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

class CustomAuthMiddleware:
    def __init__(self, get_response):       
        self.get_response = get_response

        # List of API slugs to bypass authentication
        self.bypass_slugs = [
            '/api/clear-authentication', 
        ]

    def __call__(self, request):    
        # Skip authentication for requests with paths that should bypass
        if any(request.path.startswith(slug) for slug in self.bypass_slugs):
            return self.get_response(request)
        
        auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            token = auth_header.split(' ')[1] 
            if token:                       
                try:
                    # payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                    access_token = AccessToken(token)
                    payload = access_token.payload
                    token_updated_at = 0 if payload.get("updated_at") == None else int(payload.get("updated_at", 0))
                    # request.user = payload
                    request.auth_user = User.objects.select_related('profile').get(id=payload['user_id'])
                    
                    user_profile = request.auth_user.profile
                    user_profile_updated_at = 0 if user_profile.updated_at == None else user_profile.updated_at
                    if user_profile_updated_at != token_updated_at:
                        raise AuthenticationFailed("Session expired. Please log in again.")
                    
                    request.auth_user.permissions = payload.get("permissions", [])
                    request.auth_user.is_tenant = payload.get("is_tenant", False)
                    # request.auth_user.is_superuser = payload.get("is_superuser", False)
                    request.auth_user.tenant_id = payload.get("tenant_id", None)
                    request.auth_user.tenant_parent_id = payload.get("tenant_parent_id", None)
                    request.auth_user.entity_type = payload.get("entity_type", None)
                    request.auth_user.is_admin = payload.get("is_admin", 0)
                    request.auth_user.updated_at = payload.get("updated_at", None)
                          
                except AuthenticationFailed as e:
                    return JsonResponse({'detail': str(e)}, status=401)

        return self.get_response(request)
