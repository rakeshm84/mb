from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from .serializers import UserSerializer, TenantSerializer, MyTokenObtainPairSerializer, UserProfileSerializer
from .models import Tenant, UserProfile, PermissionsMeta, Entity, EntityContentType, TenantUser
from django.db.models import OuterRef, Subquery, Value, Func, F, JSONField
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .validation_messages import ValidationMessages
from ULM.signals import set_tenant

import logging
import time
logging.basicConfig(
    level=logging.INFO,  # Set the minimum level of messages to log
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log messages to a file
        # logging.StreamHandler()  # Also print messages to the console
    ]
)

logger = logging.getLogger(__name__)

enable_logging = settings.ENABLE_APP_LOG

class AuthenticationView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

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
        
        if username:
            if any(rel.get_accessor_name() == 'profile' for rel in User._meta.related_objects):
                user = User.objects.select_related('profile').filter(username=username).first()

            if user:

                tenant_data = Tenant.objects.filter(entity_id=user.id).first()

                if tenant_data and not tenant_data.status == 1:
                    return Response(
                        {"detail": "Access denied!"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                
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

                next_url = ''
                if user.is_superuser:
                    next_url = settings.ADMIN_APP_URL
                else:
                    next_url = settings.HUMAN_APP_URL
                # Add user data to the response
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'next_url': next_url,
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
        auth_user = request.auth_user

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": auth_user.is_admin
        }
        if hasattr(user, 'profile'):
            user_data.update({
                'phone': user.profile.phone_number,
                'address': user.profile.address,
                'dob': user.profile.date_of_birth,
                'lang': user.profile.language,
                'desc': user.profile.desc,
            })

        # user_data.update({"is_admin": user.is_admin_user()})

        return Response(user_data, status=status.HTTP_200_OK)

# Create your views here.
class TestView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        # serializer = UserSerializer(data=request.data)
        # if req_user.is_tenant:
        perm = request.auth_user.has_permission("ULM.view_tenant")
            # user = User.objects.get(username=req_user.username)
            # g_permissions = user.get_group_permissions()
            # permissions = user.get_user_permissions()
            # get_all_permissions = user.get_all_permissions()
            # perm = user.has_perm("ULM.view_tenant", req_user.tenant_id)
        return Response({"message": perm}, status=status.HTTP_201_CREATED)
        # return Response({"message": "Render from the ULM service"}, status=status.HTTP_201_CREATED)
    
    def post(self, request, *args, **kwargs):
        from django.contrib.auth.models import Group, Permission
        # editor_group, created = Group.objects.get_or_create(name='Test')

        # permission = Permission.objects.get(codename='view_userprofile')
        # editor_group.permissions.add(permission)
         # content_type = ContentType.objects.get_for_model(UserProfile)
        # permission, created = Permission.objects.get_or_create(
        #     codename='can_test',
        #     name='Can Test Profiles',
        #     content_type=content_type,
        # )

        # user = User.objects.get(username='john')
        # permission = Permission.objects.get(codename='can_test')
        # user.user_permissions.add(permission)
        # user.save()

        return Response({"message": "Success"}, status=status.HTTP_201_CREATED)
    
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
    
    def get_new_access_token(self, refresh_token):
        import requests
        
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "authentication/refresh/"
        params = {
            'refresh': refresh_token
        }
        try:
            response = requests.post(api_url, params)
            return response.json()  
            # return response_content.get('access')
        except Exception as e:
            return None
    
    def get_subdomain(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0]
        return subdomain


    def get(self, request):       
        auth_cookie = request.COOKIES.get('auth_token')
        refresh_cookie = request.COOKIES.get('refresh_token')

        response = JsonResponse({"error": "Cookies not found!"}, status=401)
        if not auth_cookie:
            return response
        
        try:
            access_token = AccessToken(auth_cookie)
        except Exception as e:
            # If access token is invalid or expired, try refreshing
            if not refresh_cookie:
                return response
            
            try:
                # Attempt to refresh the access token
                refresh_token = RefreshToken(refresh_cookie)
                new_token = self.get_new_access_token(refresh_token)
                access = new_token.get('access')
                refresh = new_token.get('refresh')
                response.set_cookie(
                    'auth_token', access,
                    max_age=86400,                        
                    httponly=True,                     
                    secure=True,                      
                    samesite='None'
                )
                response.set_cookie(
                    'refresh_token', 
                    refresh,
                    max_age=86400,
                    httponly=True,                     
                    secure=True,                      
                    samesite='None'
                )
                access_token = AccessToken(access)

            except Exception as refresh_error:
                # If the refresh token is also invalid/expired
                return JsonResponse({"error": "Invalid or expired tokens!"}, status=401)
        if access_token:
            from .serializers import RefreshTokenObtainPairOnDomainShift
            platform = request.GET.get('platform')
            try:
                user_data = access_token.payload

                user_id = user_data.get('user_id')

                user = User.objects.filter(id=user_id).first()
                
                is_superuser = user.is_superuser
                is_tenant = user_data.get('is_tenant', False)
                is_human = is_tenant and user_data.get('entity_type', None) == 'human'
                parent_tenant_id = user_data.get('parent_tenant_id', False)
                permissions = user_data.get("permissions", [])
                if platform == 'admin':
                    if is_superuser:
                        return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie,"message": "Cookies set successfully!"}, status=200)
                    else:
                        tenant_user = TenantUser.objects.filter(user_id=user_id, tenant_id=0).exists()
                        
                        if tenant_user:
                            ref_token = RefreshTokenObtainPairOnDomainShift.get_token(user, 0)
                            if ref_token:
                                refresh = ref_token
                                new_access = str(refresh.access_token)
                                new_refresh = str(refresh)
                                access_token = AccessToken(new_access)
                                payload = access_token.payload
                                permissions = payload.get("permissions", [])
                                is_tenant_user = payload.get('is_tenant_user', False)
                                if is_tenant_user:
                                    new_access = str(refresh.access_token)
                                    new_refresh = str(refresh)
                                    return JsonResponse({"auth_token":new_access , "refresh_token":new_refresh, "permissions": permissions, "message": "Cookies set successfully!"}, status=200)
                    
                elif platform == 'human':
                    subdomain = request.GET.get('subdomain')
                    tenant = Tenant.objects.filter(subdomain=subdomain).first()
                    if tenant:
                        ref_token = RefreshTokenObtainPairOnDomainShift.get_token(user, tenant.id)
                        if ref_token:
                                refresh = ref_token
                                new_access = str(refresh.access_token)
                                new_refresh = str(refresh)
                                access_token = AccessToken(new_access)
                                payload = access_token.payload
                                permissions = payload.get("permissions", [])
                                is_tenant_user = payload.get('is_tenant_user', False)
                                if is_tenant_user:
                                    new_access = str(refresh.access_token)
                                    new_refresh = str(refresh)
                                    return JsonResponse({"auth_token":new_access , "refresh_token":new_refresh, "permissions": permissions, "message": "Cookies set successfully!"}, status=200)
                    # if is_human:
                    #     return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions, "message": "Cookies set successfully!"}, status=200)
                    # elif not is_tenant and parent_tenant_id:
                    #     return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions,  "message": "Cookies set successfully!"}, status=200)
                
                elif platform == 'ulm':
                    return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions, "message": "Cookies set successfully!"}, status=200)
                    # if is_superuser:
                    #     return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions,  "logged_user": "admin", "message": "Cookies set successfully!"}, status=200)
                    # elif is_human:
                    #     return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions,  "logged_user": "human", "message": "Cookies set successfully!"}, status=200)
                    # elif not is_tenant and parent_tenant_id:
                    #     return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions,  "logged_user": "human", "message": "Cookies set successfully!"}, status=200)
            except Exception as e:
                print('e', set(e))
                None
        return JsonResponse({"error": "Cookies not found!", "status": False}, status=401)
    
        # if auth_cookie:
        #     platform = request.GET.get('platform')

        #     try:
        #         access_token = AccessToken(auth_cookie)
        #         user_data = access_token.payload
            
        #         is_superuser = user_data.get('is_superuser', False)
        #         is_tenant = user_data.get('is_tenant', False)
        #         is_human = is_tenant and user_data.get('entity_type', None) == 'human'
        #         parent_tenant_id = user_data.get('parent_tenant_id', False)
        #         permissions = user_data.get("permissions", [])
        #         if platform == 'admin':
        #             if is_superuser:
        #                 return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie,"message": "Cookies set successfully!"}, status=200)
                    
        #         elif platform == 'human':
        #             if is_human:
        #                 return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions, "message": "Cookies set successfully!"}, status=200)
        #             elif not is_tenant and parent_tenant_id:
        #                 return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions,  "message": "Cookies set successfully!"}, status=200)
                
        #         elif platform == 'ulm':
        #             return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions, "message": "Cookies set successfully!"}, status=200)
        #             # if is_superuser:
        #             #     return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions,  "logged_user": "admin", "message": "Cookies set successfully!"}, status=200)
        #             # elif is_human:
        #             #     return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions,  "logged_user": "human", "message": "Cookies set successfully!"}, status=200)
        #             # elif not is_tenant and parent_tenant_id:
        #             #     return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "permissions": permissions,  "logged_user": "human", "message": "Cookies set successfully!"}, status=200)
        #     except:
        #         None

        # return JsonResponse({"error": "Cookies not found!", "status": False}, status=401)

class UserEditView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, format=None):
        try:
            # Fetch the person object using the id
            tenant_id = 0
            if self.request.auth_user.tenant_id:
                tenant_id = self.request.auth_user.tenant_id
            user = User.objects.select_related('profile').get(id=id)
            tenant_user = TenantUser.objects.filter(tenant_id=tenant_id, user_id=id).first()
            group = None

            is_admin = False
            if tenant_user:
                group=tenant_user.group_id
                is_admin = tenant_user.is_admin
            # user_group = user.groups.first()
            # group = user_group.id if user_group else None

            # Serialize the person data
            serializer = UserSerializer(user)
            profile_serializer = UserProfileSerializer(user.profile)

            user_data = serializer.data
            user_data.profile = profile_serializer.data
            user_data['role_group'] = group
            user_data['is_admin'] = is_admin

            # Return the serialized data in the response
            return Response({'user': user_data, 'profile': profile_serializer.data}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "An error occurred.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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

            userData = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
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
            
            userData.update({"is_admin": user.is_admin_user()})

            return Response({"message": "Updated successfully", "user": userData}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Person not found"}, status=status.HTTP_404_NOT_FOUND)

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q

class PersonsListView(BaseDatatableView):
    model = Tenant  # Change the model to Tenant

    columns = ['id', 'first_name', 'last_name', 'email', 'domain','subdomain', 'status', 'created_at']
    searchable_columns = ['first_name', 'last_name', 'email', 'domain','subdomain']
    order_columns = ['id', 'first_name', 'last_name', 'email', 'domain','subdomain', 'status', 'created_at']

    def get_initial_queryset(self):       
        return Tenant.objects.filter(entity='human')

    def filter_queryset(self, qs):    
        search_value = self.request.GET.get('search[value]', '').strip()
        if search_value:
            qs = qs.filter(
                Q(firstname__icontains=search_value) |   
                Q(lastname__icontains=search_value) |
                Q(email__icontains=search_value) |   
                Q(subdomain__icontains=search_value) | 
                Q(status__icontains=search_value)    
            )
        return qs
    
    def ordering(self, qs):
        order = self.request.GET.get("order[0][column]")
        direction = self.request.GET.get("order[0][dir]", "asc")
        
        if order == "first_name":
            qs = qs.order_by("firstname" if direction == "asc" else "-firstname")
        elif order == "last_name":
            qs = qs.order_by("lastname" if direction == "asc" else "-lastname")
        elif order == "email":
            qs = qs.order_by("email" if direction == "asc" else "-email")
        elif order == "subdomain":
            qs = qs.order_by("subdomain" if direction == "asc" else "-subdomain")
        elif order == "status":
            qs = qs.order_by("status" if direction == "asc" else "-status")
        elif order == "created_at":
            qs = qs.order_by("created_at" if direction == "asc" else "-created_at")

        return qs

    def prepare_results(self, qs):
        # Format the results to include the individual fields (no need for user_data)
        return [
            {
                'id': tenant.id,
                'entity_id': tenant.entity_id,
                'first_name': tenant.firstname,
                'last_name': tenant.lastname,
                'email': tenant.email,
                'db_name': tenant.db_name,
                'subdomain': tenant.subdomain + "." + settings.HUMAN_APP_DOMAIN,
                'status': tenant.status,
                'created_at': tenant.created_at,
            }
            for tenant in qs
        ]
    
class CreateUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .utils import parse_connection_string, _dsn_to_string

        entity = request.data.get('entity')
        serializer = UserSerializer(data=request.data, context={'bypass_userprofile': True})
        subdomain = request.data.get('subdomain', None)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                tenant_data = {
                    'entity': entity,
                    'entity_id': user.pk,
                    'firstname': user.first_name,
                    'lastname': user.last_name,
                    'email': user.email,
                    'name': user.username,
                    'subdomain': subdomain,
                    'status': 0
                }

                tenant_serializer = TenantSerializer(data=tenant_data)
                if tenant_serializer.is_valid():
                    tenant = tenant_serializer.save()
                    if tenant:                                                
                        # db_name = settings.MASTER_DB_NAME + '_human_' + str(tenant.pk)    
                        db_name = f"{settings.MASTER_DB_NAME}_{entity}_{tenant.pk}"
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
                        tenant.db_name = db_name
                        tenant.dsn = dsn                    
                        tenant.save()

                        tenant_user_data = {
                            "user_id": user.pk,
                            "tenant_id": tenant.pk,
                            "created_by_id": request.auth_user.id,
                            "is_admin": True,
                        }

                        created = TenantUser.objects.create(**tenant_user_data)
                        
                        data = {**tenant_data, "db_name": tenant.db_name, "dsn": tenant.dsn}
                                                
                        return Response({"message": "User created successfully!", "user_id": user.pk, "data": data, "tenant_id": tenant.pk}, status=status.HTTP_201_CREATED)
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

class ClearAuthentication(APIView):
    permission_classes = [AllowAny]


    def get(self, request):        

        response = JsonResponse({"message": "Cookies cleared successfully!"})
        # response.delete_cookie('auth_token')    
        # response.delete_cookie('refresh_token')
        response.set_cookie(
            'auth_token', '',
            max_age=0,                        
            httponly=True,                     
            secure=True,                      
            samesite='None'
        )
        response.set_cookie(
            'refresh_token', 
            '',
            max_age=0,
            httponly=True,                     
            secure=True,                      
            samesite='None'
        )
        
        return response
    
class RecentRegistrationView(BaseDatatableView):
    permission_classes = [IsAuthenticated]

    model = Tenant
    columns = ['id', 'first_name', 'last_name', 'email', 'db_name', 'status', 'created_at']
    def get_initial_queryset(self):    
        return Tenant.objects.filter(entity='human').filter(status=True)

    def filter_queryset(self, qs):
        # Apply search filter
        limit = self.request.GET.get('limit')
        if limit:
            try:
                limit = int(limit)                
                return qs.order_by('-created_at')[:limit]
            except ValueError:
                pass
        return super().paginate_queryset(qs)    

    def prepare_results(self, qs):
        # Format the results to include user_data as a dictionary
        return [
            {
                'id': tenant.id,
                'entity_id': tenant.entity_id,
                'first_name': tenant.firstname,
                'last_name': tenant.lastname,
                'email': tenant.email,
                'db_name': tenant.db_name,
                'status': tenant.status,
                'created_at': tenant.created_at,
            }
            for tenant in qs
        ]
        

class CheckPermission(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, type):
        auth_user = request.auth_user

        is_superuser = False
        is_human = False
        if type == 'admin':
            if hasattr(auth_user, 'is_superuser'):
                is_superuser = auth_user.is_superuser
            
            return Response({"success": is_superuser}, status=status.HTTP_200_OK)
        elif type == 'human':
            if hasattr(auth_user, 'is_tenant'):
                if auth_user.is_tenant:
                    if hasattr(auth_user, 'entity_type'):
                        is_human = auth_user.entity_type == 'human'
            
            return Response({"success": is_human}, status=status.HTTP_200_OK)
        
        return Response({"success": False}, status=status.HTTP_401_UNAUTHORIZED)
    
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class CreateCustomPermission(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        codename = request.POST.get('codename')
        name = request.POST.get('name')
        model_name = request.POST.get('model_name')  # e.g., "user" for the User model

        if not codename or not name or not model_name:
            return JsonResponse({"error": "Missing required fields (codename, name, model_name)."}, status=400)

        try:
            # Get the ContentType for the specified model
            content_type = ContentType.objects.get(model=model_name)

            # Create the permission
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type,
            )

            if created:
                return JsonResponse({"message": f"Permission '{name}' created successfully!"}, status=201)
            else:
                return JsonResponse({"message": f"Permission '{name}' already exists."}, status=200)

        except ContentType.DoesNotExist:
            return JsonResponse({"error": "Invalid model name provided."}, status=400)
        
class RolesListView(BaseDatatableView):
    model = Group
    columns = ['id', 'name']
    searchable_columns = ['id', 'name']
    order_columns = ['id', 'name']
    def get_initial_queryset(self):  
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at ULM RolesListView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}") 

        group_content_type = ContentType.objects.get_for_model(Group)

        tenant_id = 0
        if self.request.auth_user.tenant_id:
            tenant_id = self.request.auth_user.tenant_id

        # Filter PermissionsMeta by tenant_id and the Group content type
        permission_meta_records = PermissionsMeta.objects.filter(
            content_type=group_content_type,
            tenant_id=tenant_id
        )

        # Fetch the corresponding groups using their IDs
        group_ids = permission_meta_records.values_list('model_id', flat=True)
        
        queryset = Group.objects.filter(id__in=group_ids)
    
        if enable_logging:
            request_end_time = time.time()
            logger.info(f"Group filter Query executed and results fetched: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_end_time))}")
            logger.info(f"Time taken to fetch queryset: {request_end_time - request_start_time:.4f} seconds")
            
        return queryset

    def filter_queryset(self, qs):    
        search_value = self.request.GET.get('search[value]', '').strip()
        if search_value:
            qs = qs.filter(
                Q(id__icontains=search_value) |   
                Q(name__icontains=search_value)
            )
        return qs
    
    def ordering(self, qs):
        order = self.request.GET.get("order[0][column]")
        direction = self.request.GET.get("order[0][dir]", "asc")
        
        qs = qs.order_by("-id")
        if order == "id":
            qs = qs.order_by("id" if direction == "asc" else "-id")
        elif order == "name":
            qs = qs.order_by("name" if direction == "asc" else "-name")

        return qs

    def prepare_results(self, qs):
        # Format the results to include user_data as a dictionary
     
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"prepare_results method executed time start in ULM RolesListView at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}")
        
        data = [
            {
                'id': group.id,
                'name': group.name,
            }
            for group in qs
        ]
        
        if enable_logging:
            response_end_time = time.time()          
            # Log the total time from request start to response send
            total_time = response_end_time - request_start_time
            logger.info(f"Total time from request start to response send at ULM RolesListView: {total_time:.4f} seconds")
        
        return data
    
class PermissionListView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at ULM PermissionListView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}")
          
        tenant_id = 0
        entity_type = 'admin'
        if hasattr(request.auth_user, 'tenant_id') and request.auth_user.tenant_id:
            tenant_id = request.auth_user.tenant_id

        if hasattr(request.auth_user, 'entity_type') and request.auth_user.entity_type:
            entity_type = request.auth_user.entity_type

        
        entity = Entity.objects.filter(name=entity_type).first()
        entity_id = entity.id

        entity_content_types = EntityContentType.objects.filter(entity_id=entity_id)
        content_type_ids = entity_content_types.values_list('content_type_id', flat=True)

        # permission_content_type = ContentType.objects.get_for_model(Permission)
        # permission_meta_records = PermissionsMeta.objects.filter(
        #     content_type=permission_content_type,
        #     tenant_id=tenant_id
        # )
        # perm_ids = permission_meta_records.values_list('model_id', flat=True)

        # permissions = Permission.objects.select_related('content_type').filter(id__in=perm_ids)
        permissions = Permission.objects.select_related('content_type').filter(content_type__in=content_type_ids)
        permissions_dict = {}

        for perm in permissions:
            permission_array_item = {}
            content_type_name = perm.content_type.model
            if content_type_name == 'group':
                content_type_name = 'role'

            if content_type_name not in permissions_dict:
                permissions_dict[content_type_name] = []
            permission_array_item['id'] = perm.id
            permission_array_item['name'] = perm.name
            permission_array_item['code_name'] = perm.codename
            permissions_dict[content_type_name].append(permission_array_item)

        # Example output formatting
        formatted_permissions = []
        for content_type, perms in permissions_dict.items():
            formatted_permissions.append({
                content_type: perms
            })
        
        if enable_logging:
            request_end_time = time.time()                 
            logger.info(f"Time taken to fetch queryset and return response from PermissionListView in ULM: {request_end_time - request_start_time:.4f} seconds")    
      
       
        return JsonResponse(formatted_permissions, safe=False  )
    
class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
        Create a new group (without an id).
        """ 
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at ULM GroupCreateView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}") 
            
        return self.create_group(request)

    def create_group(self, request):
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at create_group method in  GroupCreateView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}")
            
        try:
            tenant_id = 0
            tenant_parent_id = 0
            if request.auth_user.tenant_id:
                tenant_id = request.auth_user.tenant_id
            if request.auth_user.tenant_parent_id:
                tenant_parent_id = request.auth_user.tenant_parent_id

            group_name = request.data.get("name").strip()
            permission_ids = request.data.get('permissions', [])
           
            if not group_name:
                return Response({"errors": "Group name is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            group_content_type = ContentType.objects.get_for_model(Group)
            permission_meta_records = PermissionsMeta.objects.filter(
                content_type=group_content_type,
                tenant_id=tenant_id
            )
            group_ids = []
            for record in permission_meta_records:
                group_ids.append(record.model_id)               
                
            
            existing_group_name = Group.objects.filter(id__in=group_ids)                   
                        
            group_names = []
            for group in existing_group_name:
                group_names.append(group.name.lower())
            
            check_group_name = group_name.lower()
            if check_group_name in group_names:
                return Response({"errors": {"name": "Group name already exists."}}, status=status.HTTP_400_BAD_REQUEST)
            
            set_tenant(tenant_id, tenant_parent_id)

            group = Group.objects.create(name=group_name)

            if permission_ids and group:              
                group.permissions.add(*permission_ids)

            set_tenant(None, None)
            if group:
                if enable_logging:
                    request_end_time = time.time()
                    logger.info(f"Group filter Query executed and filter and create group in ULM GroupCreateView : {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_end_time))}")
                   
                    logger.info(f"Time taken to create Group in ULM GroupCreateView: {request_end_time - request_start_time:.4f} seconds")
                
                return Response({"message": "Group created successfully!"}, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Request failed at ULM GroupCreateView: {str(e)}")
                return Response({"errors": "Group with this name already exists!"}, status=status.HTTP_409_CONFLICT)

        except Exception as e:            
            return Response({"errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CreateEntityAndAssignTable(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        entity = request.POST.get('entity')
        model_name = request.POST.get('model_name')  # e.g., "user" for the User model

        if not entity or not model_name:
            return JsonResponse({"error": "Missing required fields (entity, model_name)."}, status=400)

        try:
            entity, created = Entity.objects.get_or_create(
                name=entity
            )
            if entity:
                # Get the ContentType for the specified model
                content_type = ContentType.objects.get(model=model_name)

                # Create the permission
                entity_content_type, created = EntityContentType.objects.get_or_create(
                    entity_id=entity.id,
                    content_type=content_type
                )

                return JsonResponse({"message": f"Success!"}, status=201)
            
            else:
                return JsonResponse({"message": f"Failed!"}, status=401)

        except ContentType.DoesNotExist:
            return JsonResponse({"error": "Invalid model name provided."}, status=400)
        
class UsersListView(BaseDatatableView):
    model = User
    columns = ['id', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'tenant_users__group__name']
    searchable_columns = ['id', 'first_name', 'last_name', 'email', 'date_joined', 'tenant_users__group__name']
    order_columns = ['id', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'tenant_users__group__name']

    def get_initial_queryset(self):  
        tenant_id = self.request.auth_user.tenant_id if self.request.auth_user.tenant_id else 0

        return User.objects.filter(tenant_users__tenant_id=tenant_id).values(
            'id', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'tenant_users__group__name', 'tenant_users__is_admin'
        )

    def filter_queryset(self, qs):    
        search_value = self.request.GET.get('search[value]', '').strip()
        if search_value:
            qs = qs.filter(
                Q(first_name__icontains=search_value) |   
                Q(last_name__icontains=search_value) |
                Q(email__icontains=search_value) |   
                Q(date_joined__icontains=search_value) |
                Q(tenant_users__group__name__icontains=search_value)
            )
        return qs
    
    def ordering(self, qs):
        order = self.request.GET.get("order[0][column]")
        direction = self.request.GET.get("order[0][dir]", "asc")
        
        qs = qs.order_by("-id")

        order_map = {
            "id": "id",
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "email",
            "is_active": "is_active",
            "date_joined": "date_joined",
            "role": "tenant_users__group__name",
        }

        if order in order_map:
            field = order_map[order]
            qs = qs.order_by(field if direction == "asc" else f"-{field}")

        return qs

    def prepare_results(self, qs):
        # qs is a list of dictionaries because of .values()
        return [
            {
                'id': user['id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email'],
                'is_active': user['is_active'],
                'date_joined': user['date_joined'],
                'is_admin': user.get('tenant_users__is_admin', False),
                'role': 'Admin' if user.get('tenant_users__is_admin', False) is True else user.get('tenant_users__group__name', '')  # Use .get() to avoid KeyError
            }
            for user in qs
        ]
    
class CreateTenantUser(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            serializer = UserSerializer(data=request.data, context={'request': request, 'bypass_userprofile': True})
            role_id = request.data.get('role', None)
            tenant_id = 0

            if request.auth_user.tenant_id:
                tenant_id = request.auth_user.tenant_id

            if serializer.is_valid():
                user = serializer.save()
                if user:
                    # if role_id:
                    #     try:
                    #         group = Group.objects.get(id=role_id)
                    #         user.groups.add(group)
                    #     except Group.DoesNotExist:
                    #         return Response({"error": "Invalid group ID."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    UserProfile.objects.update_or_create(user=user)

                    TenantUser.objects.create(
                        user_id=user.id,
                        tenant_id=tenant_id,
                        created_by_id=request.auth_user.id,
                        group_id=role_id
                    )

                    return Response(
                        {'message': ValidationMessages.CREATED_SUCCESSFULLY},
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response({'message': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Log the exception here
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GroupUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at ULM GroupUpdateView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}")
        try:
            tenant_id = 0
            tenant_parent_id = 0
            if hasattr(request.auth_user, 'tenant_id') and request.auth_user.tenant_id:
                tenant_id = request.auth_user.tenant_id

            if hasattr(request.auth_user, 'tenant_parent_id') and request.auth_user.tenant_parent_id:
                tenant_parent_id = request.auth_user.tenant_parent_id
            
            group_id = id
            group = Group.objects.filter(id=group_id).first()
            
            if not group:
                return Response({"errors": {"name": "Group not found."}}, status=status.HTTP_404_NOT_FOUND)
            
            group_name = request.data.get("name").strip()

            current_updating_group = group.name
           
            if not group_name:
                return Response({"errors": "Group name is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            if group_name:
                group_content_type = ContentType.objects.get_for_model(Group)
                permission_meta_records = PermissionsMeta.objects.filter(
                    content_type=group_content_type,
                    tenant_id=tenant_id
                )
               
                group_ids = []
                for record in permission_meta_records:
                    group_ids.append(record.model_id)               
                    

                existing_group_name = Group.objects.filter(id__in=group_ids)                   
                
                group_names = []
                for g in existing_group_name:
                    group_names.append(g.name.lower())
                
                check_group_name = group_name.lower()
                current_updating_group_lower = current_updating_group.lower()
                
                if check_group_name in group_names:
                    if check_group_name == current_updating_group_lower:
                    # if Group.objects.filter(id=group_id,name__iexact=group_name).exists():  
                        group.name = group_name
                    else:
                        return Response({"errors": {"name": "Group name already exists."}}, status=status.HTTP_400_BAD_REQUEST)
                else:                    
                    group.name = group_name
                 
                permission_ids = request.data.get("permissions", [])
                if permission_ids is not None:                
                    group.permissions.clear()                
                    if permission_ids:
                        group.permissions.add(*permission_ids)
                
                group.save()
                
                if enable_logging:
                    request_end_time = time.time()
                    logger.info(f"Group update Query executed and update group in ULM GroupUpdateView : {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_end_time))}")
                   
                    logger.info(f"Time taken to update Group in ULM GroupUpdateView: {request_end_time - request_start_time:.4f} seconds")
                

                return Response({"success": "Group updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"errors":{"name": str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FetchRoleView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id): 
        user = request.auth_user
        group_id = id
        return_response = {}
        group = Group.objects.filter(id=group_id).first()
       
        if not group:
           return Response({"errors": {"name": "Group not found."}}, status=status.HTTP_404_NOT_FOUND)
       
        if group:
           return_response['group'] = {
            "id": group.id,
            "name": group.name
        }
       
        perms = group.permissions.all()
        permissions_list = []
        for permission in perms:
           permissions_list.append({
                "id": permission.id,
                "name": permission.name
            })          
                
        return_response['permissions'] = permissions_list
    
        return Response(return_response, status=status.HTTP_200_OK)

class TestFunc(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Get ContentType for the Group model
        # TenantUser.objects.create(
        #     user_id=13,
        #     tenant_id=None,
        #     created_by_id=1,
        #     is_admin=0                          
        # )

        # Tenant.objects.create(
        #     id=0,
        #     parent_id=0,
        #     entity="admin",
        #     entity_id=1,
        #     firstname="super",
        #     lastname="admin",
        #     email="admin@example.com",
        #     name="admin",
        #     subdomain=None,
        #     domain=None,
        #     db_name="mb_admin",
        #     dsn="django.db.backends.mysql://root:@localhost:3306/mb_admin",
        #     status=1
        # )

        return JsonResponse({"status": "success", "message": "Done."})

        # auth_user = request.auth_user

        # tenant = Tenant.objects.get(entity_id=auth_user.id)
        
        # email = request.data.get('email')
        # is_admin = request.data.get('is_admin', 0)
        # user = User.objects.get(email=email)

        # if user and tenant:
        #     TenantUser.objects.create(
        #         user_id=user.id,
        #         tenant_id=tenant.id,
        #         created_by_id=auth_user.id,
        #         is_admin=is_admin                          
        #     )
        #     return JsonResponse({"status": "success", "message": "Done."})
        # else:
        #     return JsonResponse({"status": "error", "message": "User not found."})

        # Stop
        # group_content_type = ContentType.objects.get_for_model(Group)
        
        # # Fetch the 'human_admin' group
        # human_admin_group = Group.objects.filter(name='human_admin').first()
        
        # if human_admin_group:
        #     group_id = human_admin_group.id
            
        #     # Filter and delete PermissionsMeta records
        #     permission_meta_records = PermissionsMeta.objects.filter(
        #         content_type=group_content_type,
        #         model_id=group_id
        #     )
        #     permission_meta_records.delete()  # Deletes all matching records
            
        #     # Delete the group itself
        #     human_admin_group.delete()
            
        #     return JsonResponse({"status": "success", "message": "Group and associated permissions deleted successfully."})
        # else:
        #     return JsonResponse({"status": "error", "message": "Group not found."})
        
class UpdateTenantUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        user = User.objects.filter(id=id).select_related('profile').first()

        if not user:
            return Response({"message": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
        
        tenant_id = 0
        if request:
            if request.auth_user:
                if request.auth_user.tenant_id:
                    tenant_id = request.auth_user.tenant_id       
    
    
        if tenant_id:
            tenant_users = TenantUser.objects.filter(tenant_id=tenant_id).select_related('user')   
            user_ids = set()         
            for tenant_user in tenant_users:
                u = tenant_user.user
                user_ids.add(u.id)
                
        new_username = request.data.get('username').strip()
        if new_username and new_username != user.username:
            user_found = User.objects.filter(username__iexact=new_username).first()
            if user_found:
                if user_found.id in user_ids:
                    return Response({"username": ValidationMessages.USERNAME_NOT_UNIQUE_CREATE_NEW_USER}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"username": ValidationMessages.USERNAME_NOT_UNIQUE}, status=status.HTTP_400_BAD_REQUEST)
            user.username = new_username         

        new_email = request.data.get('email').strip()
        if new_email and new_email != user.email:
            user_email_found = User.objects.filter(email__iexact=new_email).first()
            if user_email_found:
                if user_email_found.id in user_ids:
                    return Response({"email": ValidationMessages.EMAIL_NOT_UNIQUE_CREATE_NEW_USER}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"email": ValidationMessages.EMAIL_NOT_UNIQUE}, status=status.HTTP_400_BAD_REQUEST)
            user.email = new_email 


        # Update user fields
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = new_email
        user.username = new_username

        # Update profile fields if they exist
        if hasattr(user, 'profile'):
            user.profile.phone_number = request.data.get('phone_number', user.profile.phone_number)
            user.profile.address = request.data.get('address', user.profile.address)
            user.profile.date_of_birth = request.data.get('date_of_birth', user.profile.date_of_birth)
            user.profile.save()
        else:
            # If no profile exists, create one
            user.profile = UserProfile.objects.create(
                user=user,
                phone_number=request.data.get('phone_number'),
                address=request.data.get('address'),
                date_of_birth=request.data.get('date_of_birth'),
            )
            user.profile.save()

        user.save()

        # Update user group (auth_group)
        role_id = request.data.get('role', None)
        if role_id:
            TenantUser.objects.filter(user_id=id, tenant_id=tenant_id).update(group=role_id)
            # try:
            #     group = Group.objects.get(id=role_id)
            #     user.groups.set([group])  
            # except Group.DoesNotExist:
            #     return Response({"message": "Group does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the response data
        userData = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            # 'role_group': user.groups,
        }

        if hasattr(user, 'profile'):
            userData.update({
                'phone': user.profile.phone_number,
                'address': user.profile.address,
                'dob': user.profile.date_of_birth,
                'lang': user.profile.language,
            })

        return Response({"message": ValidationMessages.UPDATED_SUCCESSFULLY, "user": userData}, status=status.HTTP_200_OK)
class SetLanguageView(APIView): 
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        selected_language = request.data.get("language")     
        try:
            # updated_count = UserProfile.objects.filter(user=request.user.user_id).update(language=selected_language)
            user_profile, created = UserProfile.objects.get_or_create(user=request.auth_user)
            user_profile.language = selected_language
            updated = user_profile.save()
            
            if updated == 0:
                return Response(
                    {"error": "No user profile found to update."},
                    status=status.HTTP_404_NOT_FOUND
            )
            
            return Response(
                {"success": "Language updated successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetPermissions(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            permissions = request.auth_user.permissions

            return JsonResponse({"permissions": permissions}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        try:
            user_data = request.user
            auth_user = request.auth_user

            tenant_users = TenantUser.objects.filter(user=user_data.id).select_related('tenant')

            tenants_array = {}

            tenants_array['admin'] = None

            total_tenants = 0
            
            if auth_user.is_superuser:
                admin_serialize = UserSerializer(auth_user)
                tenants_array['admin'] = admin_serialize.data
            else:
                is_admin_user = TenantUser.objects.filter(user_id=user_data.id, tenant_id=0).exists()
                if is_admin_user:
                    admin = User.objects.filter(id=1, is_superuser=1, is_staff=1).first()
                    if admin:
                        admin_serialize = UserSerializer(admin)
                        tenants_array['admin'] = admin_serialize.data

            humans = {}
            businesses = {}
            if tenant_users:
                for tenant_user in tenant_users:
                    tenant_serializer = TenantSerializer(tenant_user.tenant)
                    tenant_data = tenant_serializer.data
                    if tenant_data:
                        if tenant_data.get('entity') == 'human':
                            humans[tenant_data.get('subdomain')] = tenant_data
                            total_tenants += 1
                        if tenant_data.get('entity') == 'business':
                            businesses[tenant_data.get('subdomain')] = tenant_data
                            total_tenants += 1
                    
            tenants_array['tenants'] = {"humans": humans, "businesses": businesses}
            tenants_array['total_tenants'] = total_tenants
            
            return JsonResponse({"data": tenants_array}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=401)
        
class BindExistingUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try: 
            
            if request.data.get('username'):
                user = User.objects.filter(username=request.data.get('username')).first()
            elif request.data.get('email'):
                user = User.objects.filter(email=request.data.get('email')).first()
            
            if not user:
                return Response({'message': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)

            if user:              
                role_group = request.data.get('role', None)
                tenant_id = getattr(request.auth_user, 'tenant_id', None)
                
                tenant_parent_id = 0
                if request.auth_user.tenant_parent_id:
                    tenant_parent_id = request.auth_user.tenant_parent_id
               
                # if role_group and tenant_id:
                #     set_tenant(tenant_id, tenant_parent_id)
                #     try:                        
                #         group = Group.objects.get(id=role_group)
                #         user.groups.add(group)
                #     except Group.DoesNotExist:                       
                #         return Response({"error": "Invalid group ID."}, status=status.HTTP_400_BAD_REQUEST)
                #     set_tenant(None, None)
            
          
                # Add user to TenantUser    
                TenantUser.objects.create(
                    user_id=user.id,
                    tenant_id=tenant_id,
                    created_by_id=request.auth_user.id,
                    group_id=role_group
                )
                
                return Response(
                    {'message': 'User created successfully!'},
                    status=status.HTTP_201_CREATED
                )
            else:                
                return Response({'message': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Log the exception here
            return Response(
                {"errors": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
