from .utils import make_db_connection
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

class DatabaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        # token = request.COOKIES.get('refresh_token')
        if token:
            try:
                decoded_token = AccessToken(token)
                dsn = decoded_token.payload.get('dsn')
                # print(f"Decoded Token: {dsn}")
                if dsn:
                    make_db_connection(dsn)
                else:
                    print("Error: DSN not found in token payload")
            except Exception as e:
                print(f"Error decoding token: {e}")

        response = self.get_response(request)
        return response
