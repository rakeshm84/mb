from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from .serializers import UserSerializer, TenantSerializer
from .models import Tenant, UserProfile
from django.db.models import OuterRef, Subquery, Value, Func, F, JSONField

class AuthenticationView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Perform the default token obtain behavior
        # Get the user object based on the provided credentials
        username = request.data.get('username')

        # Check if the user exists and retrieve the object
        # if username:
        #     user = User.objects.filter(username=username).first()
            
            # Check if the user is a superuser
            # if user and not user.is_superuser:
            #     return Response(
            #         {"error": "Access denied!"},
            #         status=status.HTTP_403_FORBIDDEN,
            #     )

        # Perform the default token obtain behavior
        response = super().post(request, *args, **kwargs)
        response.set_cookie(
            'auth_token', response.data.get('access'),
            max_age=86400,                        
            httponly=True,                     
            secure=True,                      
            samesite='None'
        )
        response.set_cookie(
            'refresh_token', 
            response.data.get('refresh'),
            max_age=86400,
            httponly=True,                     
            secure=True,                      
            samesite='None'
        )
        if username:
            if any(rel.get_accessor_name() == 'profile' for rel in User._meta.related_objects):
                user = User.objects.select_related('profile').filter(username=username).first()

            if user:
                is_human_tenant = request.session.get('is_human_tenant', False)

                next_url = ''
                if user.is_superuser:
                    next_url = settings.ADMIN_APP_URL
                # Add user data to the response
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'next_url': next_url,
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
        request_data = request.user  # Retrieve the authenticated user
        user = User.objects.select_related('profile').filter(id=request_data.id).first()
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

# Create your views here.
class TestView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        # serializer = UserSerializer(data=request.data)
        return Response({"message": "Render from the ULM service"}, status=status.HTTP_201_CREATED)
# Create your views here.
class SetAuthentication(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
       
        access_token = request.data.get('access_token')
        refresh_token = request.data.get('refresh_token')

        if not access_token or not refresh_token:
            return JsonResponse({"error": "Tokens are required!"}, status=400)
        
        response = JsonResponse({"message": "Cookies set successfully!"})
        response.set_cookie(
            'auth_token', access_token,
            max_age=86400,                        
            httponly=True,                     
            secure=True,                      
            samesite='None'
        )
        response.set_cookie(
            'refresh_token', 
            refresh_token,
            max_age=86400,
            httponly=True,                     
            secure=True,                      
            samesite='None'
        )
        
        return response


    def get(self, request):        
        auth_cookie = request.COOKIES.get('auth_token')
        refresh_cookie = request.COOKIES.get('refresh_token')

        if auth_cookie:
            return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie,"message": "Cookies set successfully!"})


        else:
            return JsonResponse({"error": "Cookies not found!"})

class UserEditView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, format=None):
        try:
            # Fetch the person object using the id
            user = User.objects.select_related('profile').get(id=id)

            # Serialize the person data
            serializer = UserSerializer(user)
            profile_serializer = UserProfileSerializer(user.profile)

            user_data = serializer.data
            user_data.profile = profile_serializer.data

            # Return the serialized data in the response
            return Response({'user': user_data, 'profile': profile_serializer.data}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {'detail': 'Person not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
    def post(self, request, id, *args, **kwargs):
        user = User.objects.filter(id=id).select_related('profile').first()

        if user:
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            user.email = request.data.get('email', user.email)
            if not hasattr(user, 'profile'):
                user.profile = UserProfile.objects.create(user=user)
            user.profile.phone_number = request.data.get('phone_number', user.profile.phone_number)
            user.profile.address = request.data.get('address', user.profile.address)
            user.profile.date_of_birth = request.data.get('date_of_birth', user.profile.date_of_birth)
            user.profile.desc = request.data.get('desc', user.profile.desc)
            user.save()
            user.profile.save()

            serializer = UserSerializer(user)

            is_human_tenant = request.session.get('is_human_tenant', False)

            userData = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_human_tenant': is_human_tenant,
            }

            # Check if the 'profile' related object exists
            if hasattr(user, 'profile'):
                userData.update({
                    'phone': user.profile.phone_number,
                    'address': user.profile.address,
                    'dob': user.profile.date_of_birth,
                    'lang': user.profile.language,
                    'desc': user.profile.desc,
                })

            return Response({"message": "Updated successfully", "user": userData}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Person not found"}, status=status.HTTP_404_NOT_FOUND)

from django_datatables_view.base_datatable_view import BaseDatatableView
class PersonsListView(BaseDatatableView):
    model = Tenant  # Change the model to Tenant

    columns = ['id', 'user_data', 'db_name', 'status', 'created_at']
    searchable_columns = ['user_data', 'db_name']
    order_columns = ['id', 'user_data', 'db_name', 'status', 'created_at']

    def get_initial_queryset(self):
        # Subquery to get user data as JSON
        user_subquery = User.objects.filter(id=OuterRef('entity_id')).annotate(
            data=Func(
                Value('username'),
                F('username'),
                Value('first_name'),
                F('first_name'),
                Value('last_name'),
                F('last_name'),
                Value('email'),
                F('email'),
                Value('date_joined'),
                F('date_joined'),
                function='JSON_OBJECT',
                output_field=JSONField()
            )
        ).values('data')[:1]

        # Annotate the subquery to the Tenant model
        return Tenant.objects.filter(entity='human').annotate(
            user_data=Subquery(user_subquery)
        )

    def filter_queryset(self, qs):
        # Apply search filter
        search_value = self.request.GET.get('search[value]', '').strip()
        if search_value:
            qs = qs.filter(
                Q(user_data__icontains=search_value) |
                Q(name__icontains=search_value) |
                Q(slug__icontains=search_value) |
                Q(domain__icontains=search_value)
            )
   
        return qs
    
    def ordering(self, qs):
        order = self.request.GET.get("order[0][column]")
        direction = self.request.GET.get("order[0][dir]", "asc")

        if order == "first_name":
            qs = qs.order_by("user_data__first_name" if direction == "asc" else "-user_data__first_name")
        elif order == "email":
            qs = qs.order_by("user_data__email" if direction == "asc" else "-user_data__email")
        elif order == "db_name":
            qs = qs.order_by("db_name" if direction == "asc" else "-db_name")
        elif order == "date_joined":
            qs = qs.order_by("user_data__date_joined" if direction == "asc" else "-user_data__date_joined")

        return qs

    def prepare_results(self, qs):
        # Format the results to include user_data as a dictionary
        return [
            {
                'id': tenant.id,
                'entity_id': tenant.entity_id,
                'db_name': tenant.db_name,
                'status': tenant.status,
                'user_data': tenant.user_data,  # This will be the JSON from the subquery
                'created_at': tenant.created_at,
            }
            for tenant in qs
        ]
    
class CreateUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        from .utils import parse_connection_string, _dsn_to_string

        serializer = UserSerializer(data=request.data, context={'bypass_userprofile': True})
        subdomain = request.data.get('subdomain', None)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                db_name = settings.MASTER_DB_NAME + '_human_' + str(user.pk)
                master_db_dsn_string = settings.MASTER_DB_DSN
                master_db_dsn = parse_connection_string(master_db_dsn_string)
                tenant_db_dsn = {
                    "driver": master_db_dsn['ENGINE'],
                    "host": master_db_dsn['HOST'],
                    "dbname": db_name,
                    "user": master_db_dsn['USER'],
                    "password": master_db_dsn['PASSWORD'],
                    "port": master_db_dsn['PORT'],
                }
                dsn = _dsn_to_string(tenant_db_dsn)

                tenant_data = {
                    'entity': 'human',
                    'entity_id': user.pk,
                    'firstname': user.first_name,
                    'lastname': user.last_name,
                    'email': user.email,
                    'name': user.username,
                    'subdomain': subdomain,
                    'db_name': db_name,
                    'dsn': dsn,
                    'status': 0
                }

                tenant_serializer = TenantSerializer(data=tenant_data)
                if tenant_serializer.is_valid():
                    tenant = tenant_serializer.save()
                    if tenant:
                        return Response({"message": "User created successfully!", "user_id": user.pk, "data": tenant_data, "tenant_id": tenant.pk}, status=status.HTTP_201_CREATED)
                    else:
                        Response({"message": "Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {
                            "message": "Failed to create tenant due to invalid data.",
                            "errors": tenant_serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                Response({"message": "User not saved!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {
                    "message": "Failed to create user due to invalid data.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

class UpdateUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request, id, *args, **kwargs):
        Tenant.objects.filter(id=id).update(**request.data)
        return Response({"message": "User updated successfully!"}, status=status.HTTP_200_OK)

from .utils import create_admin_db
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
            user = User.objects.create_superuser(username=username, password=password, email=email)
            # create_admin_db(user.pk)
            return JsonResponse({"message": f"Superuser {username} created successfully."}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)