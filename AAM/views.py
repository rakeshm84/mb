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
import time
logging.basicConfig(
    # level=logging.DEBUG,  # Set the minimum level of messages to log
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log messages to a file
        # logging.StreamHandler()  # Also print messages to the console
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

        payload.update({'entity': 'human'})

        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        try:
            # Make POST request to the API server
            response = requests.post(api_url, json=payload, headers=headers)

            if response.status_code == 201:
                jsonResponse = response.json()
                data = jsonResponse.get('data')
                ulm_tenant_id = jsonResponse.get('tenant_id')
                human_api_url = settings.HEEM_API_URL + "api/create/"
                human_payload = { "db_name": data['db_name'] }
                res = requests.post(human_api_url, json=human_payload)
                # logger.info(f"human_api_url {human_api_url}")
                if res.status_code == 201:
                    # logger.info(f"human_api_url res.status_code {res.status_code}")
                    jsonRes = res.json()
                    if jsonRes.get('success') == True:
                        update_res = requests.post(f"{ulm_api}update/{ulm_tenant_id}", json={"status": 1})
                        if update_res.status_code == 200:
                            return Response({"message": "Human created successfully!", "status_code": status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
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
        
class PersonsEditView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, id, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = f"{ulm_api}person/{id}/edit/"
        payload = request.data
        auth_header = {'Authorization': request.headers.get('Authorization')}
        try:
            response = requests.post(api_url, json=payload, headers=auth_header)
            return JsonResponse(response.json(), status=response.status_code)
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
        
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        try:
            response = requests.get(api_url, params=params, headers=headers)                          
            if response.status_code == 200:
                data = response.json()               
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return JsonResponse(response.json(), status=response.status_code)
        except requests.RequestException as e:           
            return JsonResponse({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    
class RecentRegistrationView(BaseDatatableView):

    def get(self, request, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "recent_registration/"
        params = {
            'limit': request.GET.get('limit', 10) 
        }
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        try:
            response = requests.get(api_url, params=params, headers=headers)                          
            if response.status_code == 200:
                data = response.json()                             
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return JsonResponse(response.json(), status=response.status_code)
        except requests.RequestException as e:           
            return JsonResponse({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
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

        page_type = request.GET.get('page_type', None)

        params = {
            'search[value]': search_value,
            'order[0][column]': order_column,
            'order[0][dir]': order_dir,
            'start': start,
            'length': length,
            'page_type': page_type
        }

        # headers = request.headers
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }

        try:
            # logger.info(f"Get roles from ULM on AAM: {api_url}")
            response = requests.get(api_url, params=params, headers=headers)       
            # logger.info(f"Get roles from ULM Response on AAM: {response.status_code}")                   
            if response.status_code == 200:
                data = response.json()                             
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:
                return Response(response.json(), 
                                status=response.status_code)
        except requests.RequestException as e:       
            # logger.info(f"Get roles Exception on AAM: {str(e)}")    
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class PermissionListView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "get-all-permissions/"

        # headers = request.headers
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }
        
        try:
            response = requests.get(api_url, headers=headers)   
            return Response(response.json(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        """
        Create a new group (without an id).
        """    
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "create_group/"          
            
        payload= request.data
        # headers = request.headers
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }

        try:        
            response =  requests.post(api_url, json=payload, headers=headers)   
            if response.status_code == 201:
                message_type = "message"
                message_or_error = response.json().get("success", "Sucessfully created.")
            else: 
                message_type = "errors"
                message_or_error = response.json().get("errors", "Something went wrong!")

        
            return Response({message_type: message_or_error}, status=response.status_code)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GroupUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = f"{ulm_api}update_group/{id}/edit/"

        payload = request.data

        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }

        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:
            message_type = "message"
            message_or_error = response.json().get("success", "Sucessfully updated.")
        else:
            message_type = "errors"
            message_or_error = response.json().get("errors", "Something went wrong!")

        return Response({message_type: message_or_error}, status=response.status_code)
    
class FetchRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id): 
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + f"get_role/{id}/"
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }

        try:
            response = requests.get(api_url, headers=headers)
               
            if response.status_code == 200:
                data = response.json()   
                                         
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return JsonResponse(response.json(), status=response.status_code)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
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
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }
        try:
            ulm_api = settings.ULM_API_URL + "api/"
            api_url = ulm_api + "set-language/" 
            params = {
                'selected_language': selected_language
            }
            response = requests.post(api_url, json=params, headers=headers)  
            
            if response.status_code == 200:
                data = response.json()
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:
                data = response.json()
                return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class EditProfile(APIView):

    permission_classes = [AllowAny]

    def post(self, request, id, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = f"{ulm_api}person/{id}/edit/"
        payload = request.data
        auth_header = {'Authorization': request.headers.get('Authorization')}
        try:
            response = requests.post(api_url, json=payload, headers=auth_header)
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Failed to connect to the API server.", "details": str(e)}, status=503)
        
class UsersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "get_users/"

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

        # headers = request.headers
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }

        try:
            response = requests.get(api_url, params=params, headers=headers)                          
            if response.status_code == 200:
                data = response.json()                             
                return JsonResponse(data, status=status.HTTP_200_OK)
            elif response.status_code == 403:
                data = response.json() 
                return Response(data, status=status.HTTP_403_FORBIDDEN)
            else:
                return JsonResponse(response.json(), status=response.status_code)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class UserCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "create-tenant-user/"
        payload = request.data

        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            return JsonResponse(response.json(), status=response.status_code)
            
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Failed to connect to the API server.", "details": str(e)}, status=503)
        
class UserEditView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, format=None):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + f"person/{id}/edit/"
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }

        params = {"permission": "user.can_edit"}

        try:
            response = requests.get(api_url, params=params, headers=headers)
               
            if response.status_code == 200:
                data = response.json()   
                                         
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return JsonResponse(response.json(), status=response.status_code)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = f"{ulm_api}user/{id}/edit/"
        payload = request.data
        payload.update({"permission":"user.can_edit"})
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Failed to connect to the API server.", "details": str(e)}, status=503)
        
class BindExistingUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = f"{ulm_api}bind-user/"
        
        token = ''
        auth_header = request.headers.get('Authorization')    
        if auth_header:            
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]
                token = token   
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',          
        }
        
        data = request.data
        
        try:
         
            response = requests.post(api_url, json=data, headers=headers)
          
            if response.status_code == 201:      
                return JsonResponse(response.json(), status=response.status_code)
            else:
                return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"message": "Failed to connect to the API server.", "details": str(e)}, status=503)

