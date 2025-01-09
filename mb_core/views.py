from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.http import JsonResponse

class AuthenticationView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Perform the default token obtain behavior
        # Get the user object based on the provided credentials
        username = request.data.get('username')

        # Check if the user exists and retrieve the object
        if username:
            user = User.objects.filter(username=username).first()
            
            # Check if the user is a superuser
            if user and not user.is_superuser:
                return Response(
                    {"error": "Access denied!"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Perform the default token obtain behavior
        response = super().post(request, *args, **kwargs)

        if username:
            if 'profile' in User._meta.related_objects:
                user = User.objects.select_related('profile').filter(username=username).first()

            if user:
                is_human_tenant = request.session.get('is_human_tenant', False)
                # Add user data to the response
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_human_tenant': is_human_tenant,
                }

                # Check if the 'profile' related object exists
                if hasattr(user, 'profile'):
                    response.data['user'].update({
                        'phone': user.profile.phone_number,
                        'address': user.profile.address,
                        'dob': user.profile.date_of_birth,
                        'lang': user.profile.language,
                        'desc': user.profile.desc,
                    })
        return response
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Retrieve the authenticated user
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        if hasattr(user, 'profile'):
            user_data.update({
                'phone': user.profile.phone_number,
                'address': user.profile.address,
                'dob': user.profile.date_of_birth,
                'lang': user.profile.language,
                'desc': user.profile.desc,
            })
        return Response(user_data, status=status.HTTP_200_OK)
    
class TestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, app_name, table_name, field, value):
        from django.apps import apps

        try:
            model = apps.get_model(app_name, table_name)
            filter_kwargs = {field: value}
            record = model.objects.filter(**filter_kwargs).values()

            return JsonResponse(list(record), safe=False)
        except LookupError:
            return JsonResponse({"error": "Invalid table name"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
class Test2View(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db import connection
        from django.db.utils import ProgrammingError

        with connection.cursor() as cursor:
            try:
                query = request.data.get("query", None)
                if not query:
                    return JsonResponse({'error': 'Invalid Data'}, safe=False) 
                cursor.execute(query)
                row = cursor.fetchall()
                return JsonResponse(list(row), safe=False)
            except ProgrammingError as e:
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_superuser(request):
    if request.method == "POST":
        try:
            
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")

            # Validate input
            if not username or not password:
                return JsonResponse({"error": "Username and password are required."}, status=400)

            # Check if superuser already exists with the same username
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "User already exists."}, status=400)

            # Create the superuser
            User.objects.create_superuser(username=username, password=password, email=email)
            return JsonResponse({"message": f"Superuser {username} created successfully."}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)