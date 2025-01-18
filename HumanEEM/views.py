from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utils import create_db, run_migrations
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
            try:
                run_migrations(human_db)
                return Response({"message": "Created Successfully", "success": True}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"message": "Error running migrations", "success": False}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)