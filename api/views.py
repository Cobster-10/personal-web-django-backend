from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, NoteSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Note

import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime

if not firebase_admin._apps:
    print("initializing firebase")    
    cred = credentials.Certificate(r"C:\Users\cobyk\Documents\CODE\Projects\PersonalWebsite\personalDjango\backend\serviceAccountKey.json.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'cobywebsite-85b1b.appspot.com'
    })

db = firestore.client()
bucket = storage.bucket()


# Create your views here.

class getDatabase(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            jsonProjects = []
            projects = db.collection("Projects").stream()
            for project in projects:
                
                project_data = project.to_dict()
                image_location = project_data.get('image')
                if image_location:
                    
                    blob = bucket.blob(image_location)
                    expiration_time = datetime.timedelta(minutes=30)
                    download_url = blob.generate_signed_url(expiration_time)
                    project_data['image'] = download_url 
                else:
                    project_data['image'] = None

                jsonProjects.append(project_data)
            
            return Response(jsonProjects, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    
class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)
    
    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)

class NoteListDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)
    
    
    
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

