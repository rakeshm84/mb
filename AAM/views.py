from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import requests
from django.conf import settings
from django.http import JsonResponse
from .serializers import TenantSerializer
from .models import Tenant
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
import logging
from django.db import connection

logging.basicConfig(
    level=logging.DEBUG,  # Set the minimum level of messages to log
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log messages to a file
        logging.StreamHandler()  # Also print messages to the console
    ]
)
logger = logging.getLogger(__name__)
# Create your views here.
class TestView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost';")
                cursor.execute(f"FLUSH PRIVILEGES;")
                print(f"Success")
                return Response({"message": "Sucess"}, status=status.HTTP_201_CREATED)
            except:
                print(f"Error")
                return Response({"message": "Error"}, status=status.HTTP_201_CREATED)
                return
        # serializer = UserSerializer(data=request.data)
        return Response({"message": "Render from the AAM service"}, status=status.HTTP_201_CREATED)

class Create(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "create/"
        payload = request.data

        try:
            # Make POST request to the API server
            response = requests.post(api_url, json=payload)

            if response.status_code == 201:
                jsonResponse = response.json()
                data = jsonResponse.get('data')
                ulm_tenant_id = jsonResponse.get('tenant_id')
                logger.info(f"ulm_tenant_id {ulm_tenant_id}")
                tenant_serializer = TenantSerializer(data=data)
                if tenant_serializer.is_valid():
                    logger.info(f"tenant_serializer valid")
                    tenant = tenant_serializer.save()
                    if tenant:
                        logger.info(f"tenant_id {tenant.pk}")
                        human_api_url = settings.HEEM_API_URL + "api/create/"
                        human_payload = { "db_name": tenant.db_name }
                        res = requests.post(human_api_url, json=human_payload)
                        if res.status_code == 201:
                            logger.info(f"human_api_url OK")
                            jsonRes = res.json()
                            if jsonRes.get('success') == True:
                                logger.info(f"human_api_url Success true")
                                Tenant.objects.filter(id=tenant.pk).update(status=1)
                                update_res = requests.post(f"{ulm_api}update/{ulm_tenant_id}", json={"status": 1})
                                if update_res.status_code == 200:
                                    logger.info(f"update_res OK")
                                    return Response({"message": "Human created successfully!"}, status=status.HTTP_201_CREATED)
                                else:
                                    return Response({"message": "Something went wrong1!"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"message": jsonRes.get('message')}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({"message": "Something went wrong2!"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"message": "Something went wrong3!"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {
                            "message": "Failed to create tenant due to invalid data.",
                            "errors": tenant_serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Return the API response to the client
            return JsonResponse({
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('Content-Type', '').startswith('application/json') else response.text
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Failed to connect to the API server.", "details": str(e)}, status=503)

class PersonsView(BaseDatatableView):
   
    model = Tenant
    columns = ['id', 'first_name', 'last_name', 'email', 'db_name', 'status', 'created_at']
    searchable_columns = ['first_name', 'last_name', 'email', 'db_name']
    order_columns = ['id', 'first_name', 'last_name', 'email', 'db_name', 'status', 'created_at']

    def get_initial_queryset(self):       
        return Tenant.objects.all()

    def filter_queryset(self, qs):    
        search_value = self.request.GET.get('search[value]', '').strip()
        if search_value:
            qs = qs.filter(
                Q(firstname__icontains=search_value) |   
                Q(lastname__icontains=search_value) |
                Q(email__icontains=search_value) |   
                Q(db_name__icontains=search_value) | 
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
        elif order == "db_name":
            qs = qs.order_by("db_name" if direction == "asc" else "-db_name")
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
    
class RecentRegistrationView(BaseDatatableView):
    model = Tenant  # Change the model to Tenant
    columns = ['id', 'first_name', 'last_name', 'email', 'db_name', 'status', 'created_at']
    def get_initial_queryset(self):       
        return Tenant.objects.filter(status=True)

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