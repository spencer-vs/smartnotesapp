from django.shortcuts import render
from .serializers import NoteSerializer, ContactSerializer, TaskSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Note, Contact
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from django.db.models import Q
from openai import OpenAI
from django.http import JsonResponse
import os
from groq import Groq
from .models import Task

# Create your views here.

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_notes(request):
    query = request.GET.get('q', '')
    notes = Note.objects.filter(
        user=request.user
    ).filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    ).order_by('modified_at')
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)


class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Note.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).order_by("-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        
class ContactListCreate(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NoteDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()



class NoteUpdateView(generics.UpdateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)


class NoteDetailView(generics.RetrieveAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user, is_deleted=False)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request, pk):
    try:
        task = Task.objects.get(id=pk, user=request.user, is_deleted=False)
        serializer = TaskSerializer(task)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception as e:
        print("Error:", e)
        return JsonResponse({'error': 'Server error'}, status=500)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    try:
        title = request.data.get("title")
        task = request.data.get("task")
        print("API KEY:", os.environ.get('GROQ_API_KEY'))
        if not title or not task:
            return JsonResponse({'error': 'Missing data'}, status=400)
        todo_list = generate_todo_list(task)
        if not todo_list:
            return JsonResponse({'error': 'Could not generate To Do list'}, status=500)
        new_todo = Task.objects.create(
            user=request.user,
            list=todo_list
        )
        return JsonResponse({'content': todo_list}, status=201)
    except Exception as e:
        print("error:", e)
        return JsonResponse({'error': 'Server error'}, status=500)
        
    
    


def generate_todo_list(user_input):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Groq API key not found")
            return None
        
        
        
        client = Groq(api_key=api_key)
        prompt = f"""
        In tabular form create a timetable for the items provided in the list, it should contain hours, days and name of activity and should start a day after the user creates timetable.
        """
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("Groq error:", e)
        return None



  



# def generate_todo_list(user_input):
    
    
    
#     try:
        
#         client = OpenAI(
#             api_key=os.environ.get("GROQ_API_KEY"),
#             base_url="https://api.groq.com/openai/v1",   # ← fixed
#         )
#         prompt = f"""
#         Create a timetable from the following tasks:
#         {user_input}
#         Spread it across 7 days with proper hours.
#         Output only the timetable, no extra explanation.
#         """
#         completion = client.chat.completions.create(
#             model="llama3-70b-8192",           # or "mixtral-8x7b-32768", "gemma2-9b-it", etc.
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ],  temperature=0.7,
#             max_tokens=1200,
#         )
#         return completion.choices[0].message.content.strip()
#     except Exception as e:
#         import traceback
#         print("Error generating timetable:")
#         traceback.print_exc()               # ← shows full stack trace in server logs
#         return None

