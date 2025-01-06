from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserSerializer, TenantSerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utilities import create_tenant_db, _dsn_to_string
from mb_core.models import UserProfile, Tenant
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery, Value, Func, F, JSONField

class CreateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # serializer = UserSerializer(data=request.data)
        serializer = UserSerializer(data=request.data, context={'bypass_userprofile': True})
        if serializer.is_valid():
            user = serializer.save()
            if user:
                db_name = settings.MASTER_DB_NAME + '_tenant_person_' + str(user.username)
                dsn = _dsn_to_string({'dbname': db_name})
                tenant_data = {
                    'entity': 'human',
                    'entity_id': user.pk,
                    'name': user.username,
                    'slug': user.username,
                    'db_name': db_name,
                    'dsn': dsn,
                    'status': 1
                }
                tenant_serializer = TenantSerializer(data=tenant_data)
                if tenant_serializer.is_valid():
                    tenant = tenant_serializer.save()
                    if tenant:
                        create_tenant_db(tenant.pk)
                        return Response({"message": "User created successfully!", "user_id": user.id}, status=status.HTTP_201_CREATED)
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

class SetLanguageView(APIView): 
    permission_classes = [IsAuthenticated]  

    def post(self, request):     
        selected_language = request.data.get("language")        
        supported_languages = settings.SUPPORTED_LANGUAGES
        if selected_language not in supported_languages:
            return Response(
                {"error": "Unsupported language."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)  
            user_profile.language = selected_language
            user_profile.save()
            return Response(
                {"success": "Language updated successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class TenantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):       
        search_query = request.GET.get('search', '')  # Get the 'search' query parameter
        # tenants = Tenant.objects.all()
        tenants = Tenant.objects.filter(
            entity='user'
        ).annotate(
            user_data=Subquery(
                User.objects.filter(id=OuterRef('entity_id')).annotate(
                    data=Func(
                        Value('username'),
                        F('username'),
                        Value('first_name'),
                        F('first_name'),
                        Value('last_name'),
                        F('last_name'),
                        Value('email'),
                        F('email'),
                        function='JSON_OBJECT',
                        output_field=JSONField()
                    )
                ).values('data')[:1]
            )
        )

        if search_query:
            # Use Q objects for case-insensitive search in multiple fields
            tenants = tenants.filter(
                Q(name__icontains=search_query) |
                Q(slug__icontains=search_query) |
                Q(db_name__icontains=search_query)
            )

        # Serialize and return JSON response
        tenant_data = list(tenants.values('id', 'entity_id', 'name', 'slug', 'db_name', 'created_at', 'status', 'user_data'))
        return JsonResponse({'persons': tenant_data})
    
class TenantEditView(APIView):
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

            userData = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
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
        
class PersonsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from django.db.models import OuterRef, Subquery, Value, Func, F, JSONField, Q
        from rest_framework.pagination import PageNumberPagination
        from rest_framework.response import Response
        import json
        
        # Parse request parameters
        server_side = request.GET.get('serverSide', 'false') == 'true'
        page = int(request.GET.get('page', 1)) if server_side else None
        page_size = int(request.GET.get('page_size', 10)) if server_side else None
        filters = json.loads(request.GET.get('filters', '[]'))
        global_filter = request.GET.get('searchBy', '')
        sorting = json.loads(request.GET.get('sorting', '[]'))

        # Base queryset
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
                function='JSON_OBJECT',
                output_field=JSONField()
            )
        ).values('data')[:1]

        tenants = Tenant.objects.filter(entity='human').annotate(
            user_data=Subquery(user_subquery)
        )

        # Build filters
        if filters:
            filter_query = Q()
            for filter_item in filters:
                field = filter_item.get('field')  # Use 'field' instead of 'id' for clarity
                value = filter_item.get('value')
                operation = filter_item.get('operation', 'icontains')
                
                if field and value:
                    if operation == 'exact':
                        filter_query &= Q(**{f"user__{field}__exact": value})
                    elif operation == 'icontains':
                        filter_query &= Q(**{f"user__{field}__icontains": value})
                    elif operation == 'gte':
                        filter_query &= Q(**{f"user__{field}__gte": value})
                    elif operation == 'lte':
                        filter_query &= Q(**{f"user__{field}__lte": value})
            
            tenants = tenants.filter(filter_query)

        # Global search
        if global_filter:
            tenants = tenants.filter(
                Q(user_data__icontains=global_filter) |
                Q(name__icontains=global_filter) |
                Q(slug__icontains=global_filter) |
                Q(domain__icontains=global_filter)
            )

        # Sorting
        if sorting:
            sort_fields = []
            for sort_item in sorting:
                field = sort_item.get('field')
                direction = sort_item.get('direction', 'asc')
                if field:
                    if field in ['username', 'first_name', 'last_name', 'email']:  # Handle user fields
                        field = f"user_data__{field}"
                    sort_field = field if direction == 'asc' else f"-{field}"
                    sort_fields.append(sort_field)
            if sort_fields:
                tenants = tenants.order_by(*sort_fields)

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(tenants, request)

        # Serialize results
        serializer = TenantSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

from django_datatables_view.base_datatable_view import BaseDatatableView

class PersonsDTView(BaseDatatableView):
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
