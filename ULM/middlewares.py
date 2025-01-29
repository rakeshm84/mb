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

    def __call__(self, request):
        # First check if Authorization header exists       
        auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            token = auth_header.split(' ')[1] 
            if token:                       
                try:
                    # payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                    access_token = AccessToken(token)
                    payload = access_token.payload
                    # request.user = payload
                    request.auth_user = User.objects.get(id=payload['user_id'])
                    request.auth_user.permissions = payload.get("permissions", [])
                    request.auth_user.is_tenant = payload.get("is_tenant", False)
                    # request.auth_user.is_superuser = payload.get("is_superuser", False)
                    request.auth_user.tenant_id = payload.get("tenant_id", None)
                    request.auth_user.tenant_parent_id = payload.get("tenant_parent_id", None)
                    request.auth_user.entity_type = payload.get("entity_type", None)
                    request.auth_user.is_admin = payload.get("is_admin", 0)
                          
                except AuthenticationFailed:
                    return JsonResponse({'detail': 'Invalid token or authentication error'}, status=401)

        return self.get_response(request)
