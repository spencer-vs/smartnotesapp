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
from .models import Task, Lecture
import traceback
import assemblyai as aai
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import uuid
import threading

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
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    try:
        title = request.data.get("title")
        task_input = request.data.get("task")
        # task_id = request.data.get(id=id)
        # Task.objects.get(id=task_id)
       # print("API KEY:", os.environ.get('GROQ_API_KEY'))
        if not title or not task_input:
            return JsonResponse({'error': 'Missing data'}, status=400)
        todo_list = generate_todo_list(task_input)
        if not todo_list:
            return JsonResponse({'error': 'Could not generate To Do list'}, status=500)
        new_todo = Task.objects.create(
           
            user=request.user,
            todo_list=todo_list,
            todo_title=title
        )
        new_todo.save()
        return JsonResponse({
            'id': new_todo.id,
            'todo_list': new_todo.todo_list,
            'todo_title': new_todo.todo_title
            
            }, status=201)
    except Exception as e:
        print("error:", e)
        return JsonResponse({'error': 'Server error'}, status=500)
        
    
    


def generate_todo_list(user_input):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            api_key = api_key.strip()
        if not api_key:
            print("❌ Groq API key not found")
            return None
        client = Groq(api_key=api_key)
        prompt = f"""
        Create a simple todo for:
        {user_input}
        it should be simple, each item should be numbered and contain a time and day, it should be spread according to the days of the week depending on the number of items and should only contain items from {user_input}.
        """
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Groq error:")
        traceback.print_exc()   # VERY IMPORTANT
        return None
    
    
    
    
# ✅ GET SINGLE TASK
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user, is_deleted=False)
        return JsonResponse({
            "id": task.id,
            "todo_title": task.todo_title,
            "todo_list": task.todo_list
        })
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error'}, status=500)
# ✅ GET ALL TASKS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_task(request):
    try:
        tasks = Task.objects.filter(user=request.user).order_by('-id')
        data = [
            {
                "id": task.id,
                "todo_title": task.todo_title,
                "todo_list": task.todo_list
            }
            for task in tasks
        ]
        return JsonResponse(data, safe=False)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error'}, status=500)
# ✅ UPDATE TASK
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
        todo_title = request.data.get("todo_title")
        todo_list = request.data.get("todo_list")
        if todo_title:
            task.todo_title = todo_title
        if todo_list:
            task.todo_list = todo_list
        task.save()
        return JsonResponse({
            "id": task.id,
            "todo_title": task.todo_title,
            "todo_list": task.todo_list
        }, status=200)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lecture_detail(request, id):
    try:
        lecture = Lecture.objects.get(id=id, user=request.user, is_deleted=False)
        return JsonResponse({
            "id": lecture.id,
            "lecture": lecture.lecture,
            "created_at": lecture.created_at
        })
    except Lecture.DoesNotExist:
        return JsonResponse({"error": "Lecture does not exist"}, status=404)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"error": "Server Error"}, status=500)
        
  


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_lectures(request):
    try:
        lectures = Lecture.objects.filter(user=request.user, is_deleted=False).order_by('-id')
        data = [
            {
                "id": lecture.id,
                "lecture": lecture.lecture,
                "created_at": lecture.created_at
            }
            for lecture in lectures
        ]
        return JsonResponse(data, safe=False)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error'}, status=500)




@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_audio(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)
    try:
        print("USER:", request.user)
        print("AUTH:", request.user.is_authenticated)
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return JsonResponse({"error": "No audio file"}, status=400)
        folder = os.path.join(settings.MEDIA_ROOT, "audio")
        os.makedirs(folder, exist_ok=True)
       # file_name = f"{uuid.uuid4()}.webm"
        # # file_path = os.path.join(folder, file_name)
        # with open(file_path, "wb+") as f:
        #     for chunk in audio_file.chunks():
        #         f.write(chunk)
        # print("Audio saved at:", file_path)
        
        lecture = Lecture.objects.create(
           user=request.user,
           audio_file=audio_file,
           status="processing"
       )
        
        threading.Thread(
            target=process_audio,
            args=(lecture.id,)
        ).start()
        
       
        
        return JsonResponse(
            {
                "message": "Processing started",
                "lecture_id": lecture.id
            }, status=202
        )
    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)



def process_audio(lecture_id):
    try:
        lecture = Lecture.objects.get(id=lecture_id)
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            print("AssemblyAI key missing!")
            lecture.status = "failed"
            lecture.save()
            return
        aai.settings.api_key = api_key
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(speech_models=["universal-3-pro", "universal-2"])
        transcript = transcriber.transcribe(lecture.audio_file.path, config=config)
        if transcript.status == "error":
            print("AssemblyAI error:", transcript.error)
            lecture.status = "failed"
            lecture.save()
            return
        notes = generate_lecture_note(transcript.text)
        lecture.lecture = notes
        lecture.status = "completed"
        lecture.save()
    except Exception as e:
        print("Audio processing error:", str(e))
        traceback.print_exc()
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            lecture.status = "failed"
            lecture.save()
        except:
            pass
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lecture_status(request, id):
    try:
        lecture = Lecture.objects.get(id=id, user=request.user)
        return JsonResponse({
            "id": lecture.id,
            "status": lecture.status,
            "lecture": lecture.lecture
        })
    except Lecture.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)
    
    



def generate_lecture_note(transcription):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Groq API key not found")
            return None
        client = Groq(api_key=api_key)
        prompt = f"""
        You are an expert academic assistant.
        Convert the following transcript into well-structured lecture notes.
        REQUIREMENTS:
        - Use clear headings and subheadings
        - Use bullet points where appropriate
        - Highlight key concepts
        - Keep it concise but complete
        - Add a short summary at the end
        Transcript:
        {transcription}
        Lecture Notes:
        """
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,   # lower = more structured
            max_tokens=1200,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("Groq error:", e)
        return None
 