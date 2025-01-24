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
from .serializers import UserSerializer, TenantSerializer, MyTokenObtainPairSerializer
from .models import Tenant, UserProfile, PermissionsMeta, Entity, EntityContentType
from django.db.models import OuterRef, Subquery, Value, Func, F, JSONField

# import logging
# logging.basicConfig(
#     level=logging.DEBUG,  # Set the minimum level of messages to log
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("app.log"),  # Log messages to a file
#         logging.StreamHandler()  # Also print messages to the console
#     ]
# )

# logger = logging.getLogger(__name__)

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


    def get(self, request):       
        from rest_framework_simplejwt.tokens import AccessToken 
        auth_cookie = request.COOKIES.get('auth_token')
        refresh_cookie = request.COOKIES.get('refresh_token')
        
        if auth_cookie:
            platform = request.GET.get('platform')

            try:
                access_token = AccessToken(auth_cookie)
                user_data = access_token.payload
            
                is_superuser = user_data.get('is_superuser', False)
                is_tenant = user_data.get('is_tenant', False)
                is_human = is_tenant and user_data.get('entity_type', None) == 'human'
                parent_tenant_id = user_data.get('parent_tenant_id', False)
                if platform == 'admin':
                    if is_superuser:
                        return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie,"message": "Cookies set successfully!"}, status=200)
                    
                elif platform == 'human':
                    if is_human:
                        return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie,"message": "Cookies set successfully!"}, status=200)
                    elif not is_tenant and parent_tenant_id:
                        return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "message": "Cookies set successfully!"}, status=200)
                
                elif platform == 'ulm':
                    if is_superuser:
                        return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "logged_user": "admin", "message": "Cookies set successfully!"}, status=200)
                    elif is_human:
                        return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "logged_user": "human", "message": "Cookies set successfully!"}, status=200)
                    elif not is_tenant and parent_tenant_id:
                        return JsonResponse({"auth_token":auth_cookie ,"refresh_token":refresh_cookie, "logged_user": "human", "message": "Cookies set successfully!"}, status=200)
            except:
                None

        return JsonResponse({"error": "Cookies not found!", "status": False}, status=401)

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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        from .utils import parse_connection_string, _dsn_to_string

        serializer = UserSerializer(data=request.data, context={'bypass_userprofile': True})
        subdomain = request.data.get('subdomain', None)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                tenant_data = {
                    'entity': 'human',
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
                        db_name = settings.MASTER_DB_NAME + '_human_' + str(tenant.pk)                     
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
        return Group.objects.filter(id__in=group_ids)

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
        
        if order == "id":
            qs = qs.order_by("id" if direction == "asc" else "-id")
        elif order == "name":
            qs = qs.order_by("name" if direction == "asc" else "-name")

        return qs

    def prepare_results(self, qs):
        # Format the results to include user_data as a dictionary
        return [
            {
                'id': group.id,
                'name': group.name,
            }
            for group in qs
        ]
    
class PermissionListView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):        
        tenant_id = 0
        entity_type = 'admin'
        if request.auth_user.tenant_id:
            tenant_id = self.request.auth_user.tenant_id

        if request.auth_user.entity_type:
            entity_type = self.request.auth_user.entity_type

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
            permissions_dict[content_type_name].append(permission_array_item)

        # Example output formatting
        formatted_permissions = []
        for content_type, perms in permissions_dict.items():
            formatted_permissions.append({
                content_type: perms
            })
       
        return JsonResponse(formatted_permissions, safe=False  )
    
class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
        Create a new group (without an id).
        """     
        return self.create_group(request)

    def create_group(self, request):
        from ULM.signals import set_tenant
        try:
            tenant_id = 0
            tenant_parent_id = 0
            if request.auth_user.tenant_id:
                tenant_id = request.auth_user.tenant_id
            if request.auth_user.tenant_parent_id:
                tenant_parent_id = request.auth_user.tenant_parent_id

            group_name = request.data.get("name")
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
                return Response({"message": "Group created successfully!"}, status=status.HTTP_201_CREATED)
            else:
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
    columns = ['id', 'first_name', 'last_name', 'email', 'is_active', 'date_joined']
    searchable_columns = ['id', 'first_name', 'last_name', 'email', 'date_joined']
    order_columns = ['id', 'first_name', 'last_name', 'email', 'is_active', 'date_joined']
    def get_initial_queryset(self):  
        tenant_id = 0
        if self.request.auth_user.tenant_id:
            tenant_id = self.request.auth_user.tenant_id

        return User.objects.filter(profile__tenant_id=tenant_id)


    def filter_queryset(self, qs):    
        search_value = self.request.GET.get('search[value]', '').strip()
        if search_value:
            qs = qs.filter(
                Q(first_name__icontains=search_value) |   
                Q(last_name__icontains=search_value) |
                Q(email__icontains=search_value) |   
                Q(date_joined__icontains=search_value)    
            )
        return qs
    
    def ordering(self, qs):
        order = self.request.GET.get("order[0][column]")
        direction = self.request.GET.get("order[0][dir]", "asc")
        
        if order == "first_name":
            qs = qs.order_by("first_name" if direction == "asc" else "-first_name")
        elif order == "last_name":
            qs = qs.order_by("last_name" if direction == "asc" else "-last_name")
        elif order == "email":
            qs = qs.order_by("email" if direction == "asc" else "-email")
        elif order == "is_active":
            qs = qs.order_by("is_active" if direction == "asc" else "-is_active")
        elif order == "date_joined":
            qs = qs.order_by("date_joined" if direction == "asc" else "-date_joined")

        return qs

    def prepare_results(self, qs):
        # Format the results to include user_data as a dictionary
        return [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
            }
            for user in qs
        ]
    
class CreateTenantUser(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data, context={'bypass_userprofile': True})
        role_group = request.data.get('role', None)
        tenant_id = 0

        if request.auth_user.tenant_id:
            tenant_id = request.auth_user.tenant_id

        if serializer.is_valid():
            user = serializer.save()
            if user:
                try:
                    group = Group.objects.get(id=role_group)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    return Response({"error": "Invalid group ID."}, status=400)
                
                profile, created = UserProfile.objects.update_or_create(
                    user=user,
                    defaults={'tenant_id': tenant_id}
                )
                return Response(
                    {'message': 'User created successfully!'},
                    status=201
                )
            else:
                return Response({'message': 'Something went wrong!'}, status=400)
        else:
            return Response(serializer.errors, status=400)

class GroupUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        
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
            
            group_name = request.data.get("name")
            if group_name:
                group.name = group_name
            
            permission_ids = request.data.get("permissions", [])
            if permission_ids is not None:                
                group.permissions.clear()                
                if permission_ids:
                    group.permissions.add(*permission_ids)
            
            group.save()

            return Response({"success": "Group updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"errors":{"name": str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FetchRoleView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, id): 
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