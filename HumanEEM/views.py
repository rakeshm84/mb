from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utils import create_db, run_migrations
from django.conf import settings
import requests
from django.http import JsonResponse

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

        headers = request.headers

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
        
class PermissionListView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        ulm_api = settings.ULM_API_URL + "api/"
        api_url = ulm_api + "get-all-permissions/"

        headers = request.headers
        
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
        headers = request.headers

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