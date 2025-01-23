from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import requests
from django.conf import settings
from django.http import JsonResponse
from .models import Tenant
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView

import logging
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
                human_api_url = settings.HEEM_API_URL + "api/create/"
                human_payload = { "db_name": data['db_name'] }
                res = requests.post(human_api_url, json=human_payload)
                logger.info(f"human_api_url {human_api_url}")
                if res.status_code == 201:
                    logger.info(f"human_api_url res.status_code {res.status_code}")
                    jsonRes = res.json()
                    if jsonRes.get('success') == True:
                        update_res = requests.post(f"{ulm_api}update/{ulm_tenant_id}", json={"status": 1})
                        if update_res.status_code == 200:
                            return Response({"message": "Human created successfully!"}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({"message": "Something went wrong1!"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"message": jsonRes.get('message')}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message": "Something went wrong2!"}, status=status.HTTP_400_BAD_REQUEST)

            # Return the API response to the client
            return JsonResponse({
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('Content-Type', '').startswith('application/json') else response.text
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Failed to connect to the API server.", "details": str(e)}, status=503)

class PersonsView(BaseDatatableView):
    
    def get(self, request, *args, **kwargs):
        # Construct the full URL for the RecentRegistrationView endpoint
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "persons/"
     
        search_value = request.GET.get('search[value]', '').strip()
        order_column = request.GET.get("order[0][column]", None)
        order_dir = request.GET.get("order[0][dir]", "asc")
        start = request.GET.get('start', 0)
        length = request.GET.get('length', 10)

        # Define the params to pass to the external API
        params = {
            'search[value]': search_value,
            'order[0][column]': order_column,
            'order[0][dir]': order_dir,
            'start': start,
            'length': length,
        }
        
        # print(params)
        try:
            response = requests.get(api_url, params=params)                          
            if response.status_code == 200:
                data = response.json()               
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return Response({"error": "Failed to fetch data", "status_code": response.status_code}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    
class RecentRegistrationView(BaseDatatableView):

    def get(self, request, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "recent_registration/"
        params = {
            'limit': request.GET.get('limit', 10) 
        }
        try:
            response = requests.get(api_url, params=params)                          
            if response.status_code == 200:
                data = response.json()                             
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return Response({"error": "Failed to fetch data", "status_code": response.status_code}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class RolesListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "get_roles/"

        search_value = request.GET.get('search[value]', '').strip()
        order_column = request.GET.get("order[0][column]", None)
        order_dir = request.GET.get("order[0][dir]", "asc")
        start = request.GET.get('start', 0)
        length = request.GET.get('length', 10)

        params = {
            'search[value]': search_value,
            'order[0][column]': order_column,
            'order[0][dir]': order_dir,
            'start': start,
            'length': length,
        }

        try:
            response = requests.get(api_url, params=params)                          
            if response.status_code == 200:
                data = response.json()                             
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return Response({"error": "Failed to fetch data", "status_code": response.status_code}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class PermissionListView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "get-all-permissions/"
        
        try:
            response = requests.get(api_url)                   
            return Response(response.json(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)