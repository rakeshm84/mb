from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utils import create_db, run_migrations
from django.conf import settings
import requests
from django.http import JsonResponse


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

enable_logging = settings.ENABLE_APP_LOG

# Create your views here.
class TestView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        # serializer = UserSerializer(data=request.data)
        return Response({"message": "Render from the HumanEEM service"}, status=status.HTTP_201_CREATED)

class CreateHuman(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        human_db = create_db(request.data.get('db_name'))
        
        if human_db:
            return Response({"message": "Created Successfully", "success": True}, status=status.HTTP_201_CREATED)
            # try:
            #     run_migrations(human_db)
            #     return Response({"message": "Created Successfully", "success": True}, status=status.HTTP_201_CREATED)
            # except Exception as e:
            #     return Response({"message": "Error running migrations", "success": False}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)
        
class RolesListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        
        
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at HumanEEM RolesListView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}")
        
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
            'length': length
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
            if enable_logging:
                request_forward_time = time.time()
                logger.info(f"Request forward to ULM from HumanEEM RolesListView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_forward_time))}")
                
            response = requests.get(api_url, params=params, headers=headers)  
            
            if enable_logging:
                request_processing_time = time.time() - request_forward_time
                logger.info(f"Response received from ULM to HumanEEM View: {request_processing_time:.4f} seconds")
                                        
            if response.status_code == 200:                
                data = response.json()  
                
                if enable_logging: 
                    response_time = time.time()
                    logger.info(f"Response sent at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(response_time))}")
                    # Log total request processing time
                    logger.info(f"Total time from request start at HumanEEM RolesListView to response send: {response_time - request_start_time:.4f} seconds")   
                                           
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return Response({"error": "Failed to fetch data", "status_code": response.status_code}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            if enable_logging:
                logger.error(f"Request to ULM API failed: {str(e)}")
                           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class PermissionListView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
                
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at HumanEEM PermissionListView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}")
        
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
            if enable_logging:
                request_forward_time = time.time()
                logger.info(f"Request forward to ULM from HumanEEM PermissionListView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_forward_time))}")
                
            response = requests.get(api_url, headers=headers)  
            
            if enable_logging:
                request_processing_time = time.time() - request_forward_time
                logger.info(f"Response received from ULM to HumanEEM PermissionListView: {request_processing_time:.4f} seconds")
                
            if enable_logging: 
                response_time = time.time()
                logger.info(f"Response sent at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(response_time))}")
                # Log total request processing time
                logger.info(f"Total time from request start at HumanEEM PermissionListView to response send: {response_time - request_start_time:.4f} seconds")    
                
                             
            return Response(response.json(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        """
        Create a new group (without an id).
        """  
        
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at HumanEEM GroupCreateView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}")  
        
        
        
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
            if enable_logging:
                request_forward_time = time.time()
                logger.info(f"Request forward to ULM from HumanEEM GroupCreateView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_forward_time))}") 
                       
            response =  requests.post(api_url, json=payload, headers=headers)   
            
            if enable_logging:
                request_processing_time = time.time() - request_forward_time
                logger.info(f"Response received from ULM to HumanEEM GroupCreateView: {request_processing_time:.4f} seconds")
                
            if response.status_code == 201:                  
                message_type = "message"
                message_or_error = response.json().get("success", "Sucessfully created.")
            else: 
                message_type = "errors"
                message_or_error = response.json().get("errors", "Something went wrong!")
                
            if enable_logging: 
                    response_time = time.time()
                    logger.info(f"Response sent at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(response_time))}")
                    # Log total request processing time
                    logger.info(f"Total time from request start to response send: {response_time - request_start_time:.4f} seconds")    
        
            return Response({message_type: message_or_error}, status=response.status_code)
        except Exception as e:
            if enable_logging:
                logger.error(f"Request to ULM API failed at HumanEEM GroupCreateView: {str(e)}")
            return Response({"errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            else:                
                return Response({"error": "Failed to fetch data", "status_code": response.status_code}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class CreateUser(APIView):
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
        
class GroupUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        
        if enable_logging:
            request_start_time = time.time()
            logger.info(f"Request Received at HumanEEM GroupUpdateView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_start_time))}") 
        
        
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

        if enable_logging:
                request_froward_time = time.time()
                logger.info(f"Request forward to ULM from HumanEEM GroupUpdateView: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(request_froward_time))}")
                
        response = requests.post(api_url, json=payload, headers=headers)
        
        if enable_logging:
            request_processing_time = time.time() - request_froward_time
            logger.info(f"Response received from ULM to HumanEEM GroupUpdateView: {request_processing_time:.4f} seconds")

        if response.status_code == 200:
            message_type = "message"
            message_or_error = response.json().get("success", "Sucessfully updated.")
        else:
            message_type = "errors"
            message_or_error = response.json().get("errors", "Something went wrong!")
            
        if enable_logging: 
            response_time = time.time()
            logger.info(f"Response sent at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(response_time))}")
            # Log total request processing time
            logger.info(f"Total time from request start at GroupUpdateView to response send: {response_time - request_start_time:.4f} seconds")   

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
                return Response({"error": "Failed to fetch data", "status_code": response.status_code}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class UpdateUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = f"{ulm_api}user/{id}/edit/"
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
            response = requests.post(api_url, params=params, headers=headers)  
            
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
        
class EditTenantUser(APIView):
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

        try:
            response = requests.get(api_url, headers=headers)
               
            if response.status_code == 200:
                data = response.json()   
                                         
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return Response({"error": "Failed to fetch data", "status_code": response.status_code}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

class EditProfile(APIView):
    permission_classes= [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = f"{ulm_api}person/{id}/edit/"
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
        
class EditUser(APIView):

    permission_classes = [AllowAny]

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

        try:
            response = requests.get(api_url, headers=headers)
               
            if response.status_code == 200:
                data = response.json()   
                                         
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:                
                return Response({"error": "Failed to fetch data", "status_code": response.status_code}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:           
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)


class GetPermissions(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = f"{ulm_api}get_user_perms/"

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
                jsonResponse = response.json()
                permissions = jsonResponse.get('permissions', [])
                return JsonResponse({"permissions": permissions}, status=response.status_code)
            else:
                return JsonResponse({"error": "Something went wrong"}, status=response.status_code)
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
                return JsonResponse({"message": "Something went wrong."}, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"message": "Failed to connect to the API server.", "details": str(e)}, status=503)
        