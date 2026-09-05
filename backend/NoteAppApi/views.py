from django.shortcuts import render
from .serializers import NoteSerializer, ContactSerializer, TaskSerializer, LectureSerializer, TutorialSerializer, SubscriptionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Note, Contact, Tutorial, Subscription,  Quiz, QuizQuestion, QuizAnswer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer
from django.db.models import Q
from datetime import datetime
from .quiz_generator import generate_quiz, save_generated_quiz
import time
from datetime import timedelta
from openai import OpenAI
from django.http import JsonResponse
import json
import os
import re
import requests
from groq import Groq
from .models import Task, Lecture
import traceback
import assemblyai as aai
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import uuid
import threading
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from .email_utils import send_brevo_email
import resend
import smtplib
import socket
from django.core.mail import get_connection
from .permissions import HasPremiumSubscription
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .subscription import user_has_premium
from django.utils import timezone
import hashlib
import hmac
# from NoteAppApi.ml.indexing import index_note

# Create your views here.

User = get_user_model()






@api_view(["GET"])
def test_email(request):
    try:
        resend.Emails.send({
        "from": settings.FROM_EMAIL,
        "to": ["isaacharu17@gmail.com"],
        "subject": "Resend Test",
        "html": "<h2>Hello from SmartNotes</h2>"
        
    })
        return JsonResponse({"success": True})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
        
    
    

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    try:
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"},
                status=400
            )
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "No account found with this email"},
                status=404
            )
        # Generate uid and token
        uidb64 = urlsafe_base64_encode(
            force_bytes(user.pk)
        )
        token = default_token_generator.make_token(user)
        # Frontend reset page URL
        reset_link = (
            f"https://smartnotesfrontend.onrender.com/"
            f"reset-password/{uidb64}/{token}/"
        )
        # Send email using Resend
        send_reset_email(
            to_email=user.email,
            reset_link=reset_link
        )
        return Response({
            "message": "Password reset email sent successfully"
        })
    except Exception as e:
        print("PASSWORD RESET ERROR:", str(e))
        return Response(
            {"error": str(e)},
            status=500
        )



resend.api_key = settings.RESEND_API_KEY


def send_reset_email(to_email, reset_link):
    resend.Emails.send({
        "from": settings.FROM_EMAIL,
        "to": [to_email],
        "subject": "Password Reset",
        "html": f"""
        <h2>Password Reset</h2>
        <p>Click the link below to reset your password</p>
        <a href="{reset_link}">{reset_link}</a>"""
    })




@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
            return JsonResponse({"error": "Invalid token"}, status=400)
        new_password = request.data.get("password")
        user.set_password(new_password)
        user.save()
        return JsonResponse({"message": "Password reset successful"})
    except Exception:
        return JsonResponse({"error": "Invalid request"}, status=400)



# client = Groq(api_key="")
# res = client.chat.completions.create(
#     model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "user", "content": "Who are you"}
#             ],
# )
# print(res.choices[0].message.content)


import socket
# Force IPv4
def force_ipv4():
    orig_getaddrinfo = socket.getaddrinfo
    def new_getaddrinfo(*args, **kwargs):
        return [res for res in orig_getaddrinfo(*args, **kwargs) if res[0] == socket.AF_INET]
    socket.getaddrinfo = new_getaddrinfo
force_ipv4()


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




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_tasks(request):
    print("SEARCH VIEW HIT")
    query = request.GET.get('q', '').strip()
    if not query:
        return Response([])
    tasks = Task.objects.filter(user=request.user)
    try:
        # Try date search
        date_obj = datetime.strptime(query, "%Y-%m-%d").date()
        tasks = tasks.filter(created_at__date=date_obj)
    except ValueError:
        # Text search
        tasks = tasks.filter(
            Q(todo_title__icontains=query) |
            Q(todo_list__icontains=query)
        )
    tasks = tasks.order_by('-created_at')
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)
from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_tutorials(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return Response([])

    tutorials = (
        Tutorial.objects
        .filter(user=request.user)
        .filter(
            Q(youtube_title__icontains=query) |
            Q(youtube_text__icontains=query)
        )
        .order_by("-created_at")
    )

    serializer = TutorialSerializer(tutorials, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_lectures(request):
    try:
        query = request.GET.get('q', '').strip()
        print("QUERY:", query)
        if not query:
            return Response([])
        lectures = Lecture.objects.filter(user=request.user)
        # ✅ Handle FULL DATE (YYYY-MM-DD)
        if len(query) == 10:
            try:
                date_obj = datetime.strptime(query, "%Y-%m-%d").date()
                lectures = lectures.filter(created_at__date=date_obj)
            except ValueError:
                lectures = Lecture.objects.none()
        # ✅ Handle YEAR-MONTH (YYYY-MM)
        elif len(query) == 7:
            lectures = lectures.filter(created_at__startswith=query)
        # ✅ Handle YEAR only (YYYY)
        elif len(query) == 4:
            lectures = lectures.filter(created_at__year=query)
        # ✅ Otherwise → TEXT SEARCH
        else:
            lectures = lectures.filter(
                Q(lecture__icontains=query)
            )
        lectures = lectures.order_by('-created_at')
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data)
    except Exception as e:
        print("SEARCH ERROR:", str(e))
        traceback.print_exc()
        return Response({"error": "Server error"}, status=500)









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

        # index_note(note)
        
        
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
@permission_classes([IsAuthenticated, HasPremiumSubscription])
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
            Create a study timetable using these tasks:
            {user_input}
            Requirements:
            - Monday to Saturday only.
            - Sunday should be excluded.
            - Every task lasts exactly 2 hours.
            - Begin each day at 8:00 AM.
            - Give a 1 hour break between tasks.
            - Each day should contain no more than two task.
            - Use this format:
            ## Monday
            8:00 AM - 10:00 AM: Task
            10:00 AM - 12:00 PM: Task
            ## Tuesday
            ...
            Return only the timetable.
            Do not write code.
            Do not explain how you generated it.
            """
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", 
                 "content": ("You are a timetable generator. " 
                             "Never write Python code"
                             "Only return a completed timetable in Markdown"
                             ),
                 },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=0.4,
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
    
    
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_task(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
        task.delete()
        return JsonResponse({"message": "Task deleted successfully"}, status=200)
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
            "title": lecture.title,
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
                "title": lecture.title,
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
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def upload_audio(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)
    try:
        print("USER:", request.user)
        print("AUTH:", request.user.is_authenticated)
        audio_file = request.FILES.get("audio")
        title = request.data.get("title", "").strip()
        if not audio_file:
            return JsonResponse({"error": "No audio file"}, status=400)
        MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50 MB

        if audio_file.size > MAX_AUDIO_SIZE:
             return JsonResponse(
            {
            "error": "Audio file is too large. "
                     "Maximum allowed size is 50 MB."
            }, status=400)
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
           title=title,
           audio_file=audio_file,
           status="processing"
       )
        
        # threading.Thread(
        #     target=process_audio,
        #     args=(lecture.id,)
        # ).start()
        
        process_audio(lecture.id)
        
       
        
        return JsonResponse(
            {
                "message": "Processing started",
                "lecture_id": lecture.id,
                "title": lecture.title,
            }, status=202
        )
    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)



def process_audio(lecture_id):
    try:
        lecture = Lecture.objects.get(id=lecture_id)
        file_path = lecture.audio_file.path
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
        short_text = transcript.text
        notes = generate_lecture_note(short_text)
        
        if not notes:
            print("Grok failed, no notes generated")
            lecture.status= "failed"
            lecture.save()
            return
    
        lecture.lecture = notes
        lecture.status = "completed"
        lecture.save()
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print('Audio file deleted successfully')
            
    except Exception as e:
        print("Audio processing error:", str(e))
        traceback.print_exc()
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            lecture.status = "failed"
            lecture.save()
        except:
            pass
        
        

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_lectures(request, id):
    try:
        lectures = Lecture.objects.get(id=id, user=request.user)
        lectures.delete()
        return JsonResponse({"message": "lecture deleted successfully"}, status=200)
    except Lecture.DoesNotExist:
        return JsonResponse({"error": "lecture not found"}, status=404)
    except Exception as e:
        print("Error deleting lecture:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": "Server Error"}, status=500)
        

        
        
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
        api_key = os.getenv("GROQ_API_KEY", " ").strip()
        print("Key Lenght", len(api_key))
        print("Last Five", repr(api_key[-5]))
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        print("TRANSCRIPT LENGTH:", len(transcription))
        print("TRANSCRIPT PREVIEW END:", transcription[-500:])
        # prompt = f"Convert this into structured lecture notes:\n{transcription[:10000]}"
        
        prompt = f"""
          Based on the generated transcript, create clear, detailed, and well-structured lecture notes.

          The notes should be easy to read and understand. Cover all relevant topics and important information from the lecture. Do not produce a simple summary. Instead, explain the concepts discussed in the lecture clearly and in enough depth for a student to learn from the notes without needing to listen to the recording again.

          the notes into meaningful sections and paragraphs, with each section focusing on a particular topic or idea from the lecture. Preserve important definitions, explanations, examples, processes, comparisons, and other relevant details mentioned by the lecturer.

          Use clear headings where appropriate, maintain a logical flow of ideas, and avoid unnecessary repetition.

          End the notes with a concise conclusion that brings together the main ideas covered in the lecture and further reading suggestions.

          Transcript:

          {transcription[:10000]}

          Lecture Notes:
          """
        
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 4000,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print("STATUS CODE:", response.status_code)
        print("RAW RESPONSE:", response.text)
        if response.status_code != 200:
            return None
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ HTTP GROQ ERROR:", repr(e))
        return None
    
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_tutorial(request, id):
    try: 
        tutorial = Tutorial.objects.get(id=id, user=request.user)
        tutorial.delete()
        return JsonResponse({"message": "Tutorial Deleted"}, status=200)
    except Tutorial.DoesNotExist:
        return JsonResponse({"error": "Tutorial not found"}, status=404)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error'}, status=500)


    
    
    
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_tutorial_details(request, id):
    try:
        tutorial = Tutorial.objects.get(
            id=id,
            user=request.user
        )
        return JsonResponse({
            "id": tutorial.id,
            "title": tutorial.youtube_title,
            "text": tutorial.youtube_text,
            "video_link": tutorial.youtube_link
        })
    except Tutorial.DoesNotExist:
        return JsonResponse(
            {"error": "Tutorial not found"},
            status=404
        )
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"error": "Server error"},
            status=500
        )
    
 

@api_view(["GET"]) 
@permission_classes([IsAuthenticated])
def get_all_tutorials(request):
    try:
        tutorials = Tutorial.objects.filter(user=request.user, is_deleted=False).order_by('-id')
        data = [
            {
                "id": tutorial.id,
                "title": tutorial.youtube_title,
                "text": tutorial.youtube_text
            }
            for tutorial in tutorials
        ]
        return JsonResponse(data, safe=False)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error'}, status=500)


 
 
 
 
 
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def generate_tutorial(request):
  
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    try:
        print("User:", request.user)
        yt_link = request.data.get('link')
        if not yt_link:
            return JsonResponse({'error': 'No YouTube link provided'}, status=400)
        print(f"Generating blog for: {yt_link}")
        # Extract video ID
        video_id = get_video_id(yt_link)
        title = get_youtube_title(video_id)
        print("Extracted video ID:", video_id)
        if not video_id:
            return JsonResponse({'error': 'Invalid YouTube URL'}, status=400)
        # Get transcript
        # transcription = transcription[:1200]
        transcription = get_transcription(video_id)
        if not transcription:
            return JsonResponse({'error': 'Transcript not available for this video'}, status=500)
        # Generate blog
        tutorial = generate_tutorial_from_transcript(transcription)
        if not tutorial:
            return JsonResponse({'error': 'Failed to generate tutorial'}, status=500)
        # Save blog to database
        new_tutorial = Tutorial.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            youtube_text=tutorial,
        )
        new_tutorial.save()
        
        
        
        return JsonResponse({'content': tutorial})
    except Exception as e:
        print("SERVER ERROR:", e)
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
# ---------------- TRANSCRIPT FUNCTIONS ---------------- #
def get_video_id(url):
    try:
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print("Video ID extraction error:", e)
        return None
    
    
def get_youtube_title(video_id):
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["title"]
        return f"YouTube Video {video_id}"
    except Exception as e:
        print("Title fetch error:", e)
        return f"YouTube Video {video_id}"
    
    
    
# ---------------- TRANSCRIPT FUNCTIONS ---------------- #
def get_transcription(video_id):
    # """Try YouTube transcript first. If unavailable, fallback to Proxy_Transcript or AssemblyAI."""
    """Attempt to retrieve a transcript using YouTubeTranscriptApi.

    If the YouTube API call fails (missing method, no transcript, etc.), we
    fall back to AssemblyAI. This version avoids using
    ``list_transcripts`` which may not exist in older installations.
    """
    proxy_transcript = get_transcription_proxy(video_id)
    if proxy_transcript:
        return proxy_transcript
    print("No transcript found")
    return None
    

    
# ---------------- TRANSCRIPTION HELPERS ---------------- #

def get_transcription_proxy(video_id):
    """Fetch transcript using RapidAPI proxy"""
    try:
        url = "https://youtube-transcript3.p.rapidapi.com/api/transcript"
        querystring = {"videoId": video_id}  # FIXED
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPID_API_KEY"),
            "X-RapidAPI-Host": "youtube-transcript3.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            #print("RAPIDAPI_KEY:", os.getenv("RAPID_API_KEY"))
            # Handle both possible formats
            if isinstance(data, dict) and "transcript" in data:
                transcript_list = data["transcript"]
            elif isinstance(data, list):
                transcript_list = data
            else:
                print("Unexpected API response:", data)
                return None
            transcript_text = " ".join(
                str(item.get("text", ""))
                for item in transcript_list
                if item.get("text") is not None
            )
            return transcript_text
        print("Proxy transcript API failed:", response.text)
    except Exception as e:
        print("Proxy transcript error:", e)
        print("Proxy status:", response.status_code)
        print("Proxy response:", response.text[:500])
    return None



#---------------- AI BLOG GENERATION ---------------- #
import time
def generate_tutorial_from_transcript(transcription):
    try:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            print("Groq API key not found")
            return None
        client = Groq(api_key=api_key)
        transcription = transcription[:1200]
        prompt = f"""
        Based on the generated transcript, create lecture notes, covering all relevant aspects of the video, it should be easily readable and well structured in paragraphs, with each paragraph explaining a particular section of the video, do not give a simple summary instead dive into deep explanations of the points mentioned in the video and finally a conclusion.
        Transcript:
        {transcription}
        Article:
        """
        for attempt in range(3):  # ✅ retry 3 times
            try:
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1000,
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"Groq attempt {attempt+1} failed:", e)
                time.sleep(2)
        return None
    except Exception as e:
        print("Groq fatal error:", e)
        return None
    
    


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    subscription, _ = Subscription.objects.get_or_create(user=request.user)
    serializer = SubscriptionSerializer(subscription)
    return Response(serializer.data)




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initialize_payment(request):
    
    if not request.user.email:
        return Response(
        {"detail": "Please add an email address before subscribing."},
        status=400
       )
        
    subscription = request.user.subscription
    
    if (
    subscription.status == "active"
    and subscription.subscription_end
    and subscription.subscription_end > timezone.now()
    ):
     return Response(
        {"detail": "You already have an active subscription."},
        status=400
     )

    
    plan_name = request.data.get("plan")

    if plan_name not in settings.PAYSTACK_PLANS:
        return Response(
            {"detail": "Invalid subscription plan."},
            status=400
        )

    plan = settings.PAYSTACK_PLANS[plan_name]

    try:
        subscription = request.user.subscription
    except Subscription.DoesNotExist:
        subscription = Subscription.objects.create(
            user=request.user
        )

    reference = f"SN-{request.user.id}-{int(timezone.now().timestamp())}"

    amount = plan["amount"] * 100

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
    "email": request.user.email,
    "amount": amount,
    "reference": reference,
    "plan": plan["code"],
    "metadata": {
        "user_id": request.user.id,
        "plan": plan_name,
    },
    "callback_url": "https://smartnotesfrontend.onrender.com/payment/callback",
    }

    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=data,
            headers=headers,
            timeout=30,
        )

        response_data = response.json()
        
        # print(
        # "PAYSTACK KEY:",
        # settings.PAYSTACK_SECRET_KEY[:12]
        # if settings.PAYSTACK_SECRET_KEY
        # else "MISSING"
        # )
        
        # print("USER:", request.user)
        # print("EMAIL:", request.user.email)
        # print("PLAN:", plan_name)
        # print("PAYSTACK STATUS:", response.status_code)
        # print("PAYSTACK RESPONSE:", response_data)

    except requests.RequestException:
        return Response(
            {"detail": "Unable to connect to Paystack."},
            status=503
        )

    if not response_data.get("status"):
        return Response(
            {
                "detail": response_data.get(
                    "message",
                    "Unable to initialize payment."
                )
            },
            status=400
        )

    subscription.paystack_reference = reference
    subscription.plan = plan_name
    subscription.save(
        update_fields=[
            "paystack_reference",
            "plan",
            "updated_at",
        ]
    )

    return Response(
        {
            "authorization_url": response_data["data"]["authorization_url"],
            "access_code": response_data["data"]["access_code"],
            "reference": reference,
        },
        status=200
    )
    
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_payment(request, reference):

    # -----------------------------------
    # Get user's subscription
    # -----------------------------------

    try:
        subscription = request.user.subscription

    except Subscription.DoesNotExist:
        return Response(
            {"detail": "Subscription not found."},
            status=404
        )

    # -----------------------------------
    # Validate payment reference
    # -----------------------------------
    
    print("========== PAYMENT VERIFICATION DEBUG ==========")
    print("User:", request.user.id)
    print("Reference from URL:", reference)
    print("Reference in database:", subscription.paystack_reference)
    print("Subscription status:", subscription.status)
    print("Subscription plan:", subscription.plan)
    print("Paystack transaction ID:", subscription.paystack_transaction_id)
    print("Paystack subscription code:", subscription.paystack_subscription_code)
    print("================================================")

    if subscription.paystack_reference != reference:
        return Response(
            {"detail": "Invalid payment reference."},
            status=400
        )

    # -----------------------------------
    # Paystack headers
    # -----------------------------------

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # -----------------------------------
    # Verify transaction with Paystack
    # -----------------------------------

    try:

        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers,
            timeout=30,
        )

        response_data = response.json()

    except requests.RequestException:

        return Response(
            {
                "detail":
                "Unable to connect to Paystack. "
                "Please try again."
            },
            status=503
        )

    # -----------------------------------
    # Check Paystack response
    # -----------------------------------

    if not response_data.get("status"):

        return Response(
            {
                "detail": response_data.get(
                    "message",
                    "Payment verification failed."
                )
            },
            status=400
        )

    transaction = response_data.get("data", {})

    payment_status = transaction.get("status")

    # -----------------------------------
    # Payment abandoned
    # -----------------------------------

    if payment_status == "abandoned":

        return Response(
            {
                "detail": (
                    "Your payment was cancelled or abandoned. "
                    "Your subscription has not been activated."
                ),
                "status": "abandoned",
            },
            status=400
        )

    # -----------------------------------
    # Payment failed
    # -----------------------------------

    if payment_status == "failed":

        return Response(
            {
                "detail": (
                    "Your payment could not be completed. "
                    "Your subscription has not been activated."
                ),
                "status": "failed",
            },
            status=400
        )

    # -----------------------------------
    # Payment not completed
    # -----------------------------------

    if payment_status != "success":

        return Response(
            {
                "detail": (
                    "Payment has not been completed yet. "
                    "Please try again."
                ),
                "status": payment_status,
            },
            status=400
        )

    # -----------------------------------
    # Successful transaction
    # -----------------------------------

    transaction_id = transaction.get("id")

    if not transaction_id:

        return Response(
            {
                "detail":
                "Paystack transaction ID was not found."
            },
            status=400
        )

    transaction_id = str(transaction_id)

    # -----------------------------------
    # IMPORTANT:
    #
    # Prevent the same payment from being
    # processed more than once.
    # -----------------------------------

    if (
        subscription.paystack_transaction_id
        and
        subscription.paystack_transaction_id == transaction_id
    ):

        print(
            "Payment already processed:",
            transaction_id
        )

        return Response(
            {
                "message":
                "Payment has already been processed.",
                "plan": subscription.plan,
                "status": subscription.status,
                "subscription_start":
                    subscription.subscription_start,
                "subscription_end":
                    subscription.subscription_end,
                "days_left":
                    subscription.days_left,
                "premium":
                    subscription.premium,
            },
            status=200
        )

    # -----------------------------------
    # Process payment
    # -----------------------------------

    try:

        # --------------------------------
        # FIRST PAYMENT
        # --------------------------------

        if not subscription.paystack_transaction_id:

            print(
                "Processing FIRST payment:",
                transaction_id
            )

            activate_subscription(
                subscription,
                transaction
            )

            message = (
                "Subscription activated successfully."
            )

        # --------------------------------
        # NEW PAYMENT
        #
        # This branch is mainly for a
        # legitimate new transaction.
        # --------------------------------

        else:

            print(
                "Processing NEW payment:",
                transaction_id
            )

            # ----------------------------
            # Don't renew a subscription
            # that has been marked as
            # non-renewing/cancelled.
            # ----------------------------

            if subscription.cancel_at_period_end:

                print(
                    "WARNING: Payment received for "
                    "a cancelled/non-renewing subscription."
                )

                return Response(
                    {
                        "message":
                        "Payment received, but the "
                        "subscription is marked as "
                        "non-renewing."
                    },
                    status=200
                )

            renew_subscription(
                subscription,
                transaction
            )

            message = (
                "Subscription renewed successfully."
            )

    except ValueError as e:

        return Response(
            {"detail": str(e)},
            status=400
        )

    # -----------------------------------
    # Return updated subscription
    # -----------------------------------

    return Response(
        {
            "message": message,
            "plan": subscription.plan,
            "status": subscription.status,
            "subscription_start":
                subscription.subscription_start,
            "subscription_end":
                subscription.subscription_end,
            "days_left":
                subscription.days_left,
            "premium":
                subscription.premium,
        },
        status=200
    )
    
    
    
    
    
    
     

def activate_subscription(subscription, transaction):

    plan = subscription.plan
    now = timezone.now()

    # -----------------------------
    # Determine subscription duration
    # -----------------------------

    if plan == "monthly":
        duration = timedelta(days=30)

    elif plan == "yearly":
        duration = timedelta(days=365)

    else:
        raise ValueError("Invalid subscription plan.")

    # -----------------------------
    # Determine subscription end
    # -----------------------------
    # If the user still has trial time remaining,
    # preserve it and add the purchased subscription
    # duration to the trial end date.
    #
    # Example:
    # Trial ends: August 30
    # Monthly plan: 30 days
    # New end: September 29
    #
    # If the trial has already expired, start the
    # purchased subscription from now.

    if subscription.trial_end and subscription.trial_end > now:

        new_subscription_end = (
            subscription.trial_end + duration
        )

    else:

        new_subscription_end = (
            now + duration
        )

    # -----------------------------
    # First activation
    # -----------------------------

    if (
        subscription.status != "active"
        or not subscription.subscription_end
        or subscription.subscription_end <= now
    ):

        subscription.status = "active"

        # The paid subscription begins when payment
        # is successfully processed.
        subscription.subscription_start = now

        subscription.subscription_end = (
            new_subscription_end
        )

    # -----------------------------
    # Existing active subscription
    # -----------------------------

    else:

        # Do not renew a subscription that has been
        # scheduled for cancellation.
        if subscription.cancel_at_period_end:

            raise ValueError(
                "Subscription is scheduled for cancellation."
            )

        # Existing active subscription:
        # preserve its remaining time and add the
        # newly purchased duration.
        subscription.subscription_end = (
            subscription.subscription_end + duration
        )

    # -----------------------------
    # Paystack transaction
    # -----------------------------

    transaction_id = transaction.get("id")

    if transaction_id:

        subscription.paystack_transaction_id = str(
            transaction_id
        )

    reference = transaction.get("reference")

    if reference:

        subscription.paystack_reference = reference

    # -----------------------------
    # Paystack customer
    # -----------------------------

    customer = transaction.get("customer", {})

    customer_id = customer.get("id")
    customer_code = customer.get("customer_code")

    if customer_code:

        subscription.paystack_customer_code = (
            customer_code
        )

    # -----------------------------
    # Paystack recurring subscription
    # -----------------------------

    if customer_id:

        plan_code = settings.PAYSTACK_PLANS[
            plan
        ]["code"]

        paystack_subscription = (
            get_paystack_subscription(
                customer_id,
                plan_code
            )
        )

        if paystack_subscription:

            subscription.paystack_subscription_code = (
                paystack_subscription.get(
                    "subscription_code",
                    ""
                )
            )

            subscription.paystack_email_token = (
                paystack_subscription.get(
                    "email_token"
                )
            )

    # -----------------------------
    # Save subscription
    # -----------------------------

    subscription.save()

    return subscription




def renew_subscription(subscription, transaction):
    now = timezone.now()

    # ---------------------------------------
    # Prevent duplicate transaction processing
    # ---------------------------------------

    transaction_id = transaction.get("id")

    if not transaction_id:
        raise ValueError(
            "Missing Paystack transaction ID."
        )

    transaction_id = str(transaction_id)

    if (
        subscription.paystack_transaction_id
        == transaction_id
    ):
        print(
            "RENEWAL ALREADY PROCESSED:",
            transaction_id
        )

        return subscription

    # ---------------------------------------
    # Determine renewal duration
    # ---------------------------------------

    if subscription.plan == "monthly":
        duration = timedelta(days=30)

    elif subscription.plan == "yearly":
        duration = timedelta(days=365)

    else:
        raise ValueError(
            "Invalid subscription plan."
        )

    # ---------------------------------------
    # Extend existing subscription
    # ---------------------------------------

    if (
        subscription.subscription_end
        and subscription.subscription_end > now
    ):
        subscription.subscription_end += duration

    else:
        subscription.subscription_end = now + duration

    subscription.status = "active"

    # ---------------------------------------
    # Save Paystack transaction
    # ---------------------------------------

    subscription.paystack_transaction_id = (
        transaction_id
    )

    subscription.save(
        update_fields=[
            "status",
            "subscription_end",
            "paystack_transaction_id",
            "updated_at",
        ]
    )

    print(
        "SUBSCRIPTION RENEWED:",
        transaction_id
    )

    return subscription



def get_paystack_subscription(customer_id, plan_code):

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(
            "https://api.paystack.co/subscription",
            params={
                "customer": customer_id
            },
            headers=headers,
            timeout=30,
        )

        response_data = response.json()

    except requests.RequestException:
        return None

    if not response_data.get("status"):
        return None

    subscriptions = response_data.get("data", [])

    for item in subscriptions:

        if item.get("plan", {}).get(
            "plan_code"
        ) == plan_code:

            return item

    return None



@api_view(["POST"])
def paystack_webhook(request):

    print("PAYSTACK WEBHOOK RECEIVED")
    print("BODY:", request.body)
    print(
        "SIGNATURE:",
        request.headers.get("x-paystack-signature")
    )

    # ---------------------------------------
    # Verify Paystack signature
    # ---------------------------------------

    signature = request.headers.get(
        "x-paystack-signature"
    )

    if not signature:
        return Response(
            {"detail": "Missing Paystack signature."},
            status=400
        )

    secret_key = settings.PAYSTACK_SECRET_KEY

    computed_signature = hmac.new(
        secret_key.encode("utf-8"),
        request.body,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(
        computed_signature,
        signature
    ):
        return Response(
            {"detail": "Invalid signature."},
            status=400
        )

    event = request.data
    event_type = event.get("event")

    # ---------------------------------------
    # Failed payment
    # ---------------------------------------

    if event_type in [
        "charge.failed",
        "invoice.payment_failed",
    ]:

        print("PAYMENT FAILED")
        print(
            "FAILED PAYMENT DATA:",
            event.get("data", {})
        )

        return Response(
            {
                "message":
                "Payment failed. Subscription was not renewed."
            },
            status=200
        )

    # ---------------------------------------
    # Ignore other events
    # ---------------------------------------

    if event_type != "charge.success":

        return Response(
            {"message": "Event ignored."},
            status=200
        )

    # ---------------------------------------
    # Successful payment
    # ---------------------------------------

    transaction = event.get("data", {})

    reference = transaction.get("reference")

    if not reference:

        return Response(
            {"detail": "Missing transaction reference."},
            status=400
        )

    # ---------------------------------------
    # Find subscription by reference
    # ---------------------------------------

    subscription = None

    try:

        subscription = Subscription.objects.get(
            paystack_reference=reference
        )

    except Subscription.DoesNotExist:

        pass

    # ---------------------------------------
    # Fallback: find by Paystack customer code
    # ---------------------------------------

    if subscription is None:

        customer = transaction.get(
            "customer",
            {}
        )

        customer_code = customer.get(
            "customer_code"
        )

        if customer_code:

            subscription = (
                Subscription.objects
                .filter(
                    paystack_customer_code=customer_code
                )
                .first()
            )

    # ---------------------------------------
    # Subscription could not be identified
    # ---------------------------------------

    if subscription is None:

        return Response(
            {
                "detail":
                "Unable to identify the SmartNotes subscription."
            },
            status=404
        )

    # ---------------------------------------
    # Process successful payment
    # ---------------------------------------

    try:

        # -----------------------------------
        # First payment
        # -----------------------------------

        if not subscription.paystack_subscription_code:

            activate_subscription(
                subscription,
                transaction
            )

            message = (
                "Subscription activated successfully."
            )

        # -----------------------------------
        # Recurring payment
        # -----------------------------------

        else:

            renew_subscription(
                subscription,
                transaction
            )

            message = (
                "Subscription renewed successfully."
            )

    except ValueError as e:

        return Response(
            {"detail": str(e)},
            status=400
        )

    # ---------------------------------------
    # Success
    # ---------------------------------------

    return Response(
        {
            "message": message,
        },
        status=200
    )



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):

    subscription = request.user.subscription

    # Make sure the user actually has an active subscription
    if not subscription.is_active:
        return Response(
            {
                "detail": "You do not have an active subscription."
            },
            status=400
        )

    # Prevent cancelling twice
    if subscription.cancel_at_period_end:
        return Response(
            {
                "detail":
                "Your subscription is already scheduled for cancellation."
            },
            status=400
        )

    # Make sure Paystack information exists
    if not subscription.paystack_subscription_code:
        return Response(
            {
                "detail":
                "We could not find your Paystack subscription."
            },
            status=400
        )

    if not subscription.paystack_email_token:
        return Response(
            {
                "detail":
                "We could not verify your Paystack subscription."
            },
            status=400
        )

    headers = {
        "Authorization":
            f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "code": subscription.paystack_subscription_code,
        "token": subscription.paystack_email_token,
    }

    try:

        response = requests.post(
            "https://api.paystack.co/subscription/disable",
            json=data,
            headers=headers,
            timeout=30,
        )

        response_data = response.json()

    except requests.RequestException:

        return Response(
            {
                "detail":
                "Unable to contact Paystack. "
                "Please try again."
            },
            status=503
        )

    # Paystack rejected the cancellation
    if not response_data.get("status"):

        return Response(
            {
                "detail":
                response_data.get(
                    "message",
                    "Unable to cancel your subscription."
                )
            },
            status=400
        )

    # --------------------------------
    # Paystack cancellation succeeded
    # --------------------------------

    subscription.cancel_at_period_end = True
    subscription.cancelled_at = timezone.now()

    subscription.save(
        update_fields=[
            "cancel_at_period_end",
            "cancelled_at",
            "updated_at",
        ]
    )

    return Response(
        {
            "message":
            "Your subscription has been cancelled. "
            "You will continue to have premium access "
            "until the end of your current billing period.",

            "status": subscription.status,

            "cancelled_at":
                subscription.cancelled_at,

            "subscription_end":
                subscription.subscription_end,

            "cancel_at_period_end":
                subscription.cancel_at_period_end,
        },
        status=200
    )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def generate_quiz_view(request):

    try:
        # -----------------------------------
        # Get request data
        # -----------------------------------

        lecture_id = request.data.get("lecture_id")
        tutorial_id = request.data.get("tutorial_id")

        difficulty = request.data.get("difficulty")
        question_type = request.data.get("question_type")

        print("QUIZ REQUEST")
        print("User:", request.user)
        print("Lecture ID:", lecture_id)
        print("Tutorial ID:", tutorial_id)
        print("Difficulty:", difficulty)
        print("Question Type:", question_type)

        # -----------------------------------
        # Validate source
        # -----------------------------------

        if not lecture_id and not tutorial_id:
            return Response(
                {
                    "error": "Please provide either lecture_id or tutorial_id."
                },
                status=400
            )

        if lecture_id and tutorial_id:
            return Response(
                {
                    "error": "Provide either lecture_id or tutorial_id, not both."
                },
                status=400
            )

        # -----------------------------------
        # Validate difficulty
        # -----------------------------------

        valid_difficulties = {
            "easy": 5,
            "mixed": 10,
            "hard": 20,
        }

        if difficulty not in valid_difficulties:
            return Response(
                {
                    "error": "Invalid difficulty. Choose easy, mixed, or hard."
                },
                status=400
            )

        # -----------------------------------
        # Validate question type
        # -----------------------------------

        valid_question_types = {
            "multiple_choice",
            "true_false",
        }

        if question_type not in valid_question_types:
            return Response(
                {
                    "error": (
                        "Invalid question type. "
                        "Choose multiple_choice or true_false."
                    )
                },
                status=400
            )

        # -----------------------------------
        # Get source content
        # -----------------------------------

        lecture = None
        tutorial = None

        if lecture_id:

            try:
                lecture = Lecture.objects.get(
                    id=lecture_id,
                    user=request.user,
                    is_deleted=False
                )

            except Lecture.DoesNotExist:
                return Response(
                    {
                        "error": "Lecture not found."
                    },
                    status=404
                )

            source_text = lecture.lecture

            if not source_text or not source_text.strip():
                return Response(
                    {
                        "error": "This lecture does not contain any content."
                    },
                    status=400
                )

        else:

            try:
                tutorial = Tutorial.objects.get(
                    id=tutorial_id,
                    user=request.user,
                    is_deleted=False
                )

            except Tutorial.DoesNotExist:
                return Response(
                    {
                        "error": "Tutorial not found."
                    },
                    status=404
                )

            source_text = tutorial.youtube_text

            if not source_text or not source_text.strip():
                return Response(
                    {
                        "error": "This tutorial does not contain any content."
                    },
                    status=400
                )

        # -----------------------------------
        # Generate quiz with AI
        # -----------------------------------

        print("🧠 Starting quiz generation...")

        quiz_data = generate_quiz(
            source_text=source_text,
            difficulty=difficulty,
            question_type=question_type,
        )

        if not quiz_data:
            return Response(
                {
                    "error": "Unable to generate quiz. Please try again."
                },
                status=500
            )

        # -----------------------------------
        # Save quiz
        # -----------------------------------

        quiz = save_generated_quiz(
            user=request.user,
            difficulty=difficulty,
            question_type=question_type,
            quiz_data=quiz_data,
            lecture=lecture,
            tutorial=tutorial,
        )

        if not quiz:
            return Response(
                {
                    "error": "Quiz was generated but could not be saved."
                },
                status=500
            )

        # -----------------------------------
        # Prepare questions for frontend
        # -----------------------------------

        questions = quiz.questions.all().order_by("order")

        question_data = []

        for question in questions:

            options = {
                "A": question.option_a,
                "B": question.option_b,
            }

            if question.option_c:
                options["C"] = question.option_c

            if question.option_d:
                options["D"] = question.option_d

            question_data.append(
                {
                    "id": question.id,
                    "order": question.order,
                    "question": question.question,
                    "options": options,
                }
            )

        # -----------------------------------
        # Return quiz
        # -----------------------------------

        return Response(
            {
                "id": quiz.id,
                "difficulty": quiz.difficulty,
                "question_type": quiz.question_type,
                "number_of_questions": quiz.number_of_questions,
                "completed": quiz.completed,
                "questions": question_data,
            },
            status=201
        )

    except Exception as e:

        print("❌ QUIZ GENERATION ERROR:", repr(e))
        traceback.print_exc()

        return Response(
            {
                "error": "An unexpected error occurred while generating the quiz."
            },
            status=500
        )
        
        
        
        
        
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def submit_quiz_view(request, quiz_id):

    try:
        # -----------------------------------
        # Get quiz
        # -----------------------------------

        try:
            quiz = Quiz.objects.get(
                id=quiz_id,
                user=request.user
            )

        except Quiz.DoesNotExist:
            return Response(
                {
                    "error": "Quiz not found."
                },
                status=404
            )

        # -----------------------------------
        # Prevent resubmission
        # -----------------------------------

        if quiz.completed:
            return Response(
                {
                    "error": "This quiz has already been completed."
                },
                status=400
            )

        # -----------------------------------
        # Get submitted answers
        # -----------------------------------

        answers = request.data.get("answers")

        if not answers:
            return Response(
                {
                    "error": "Please provide your answers."
                },
                status=400
            )

        if not isinstance(answers, dict):
            return Response(
                {
                    "error": "Answers must be provided as an object."
                },
                status=400
            )

        # -----------------------------------
        # Get quiz questions
        # -----------------------------------

        questions = quiz.questions.all().order_by("order")

        if not questions.exists():
            return Response(
                {
                    "error": "This quiz has no questions."
                },
                status=400
            )

        # -----------------------------------
        # Score quiz
        # -----------------------------------

        score = 0
        results = []

        for question in questions:

            question_id = str(question.id)

            selected_answer = answers.get(question_id)

            if selected_answer is None:
                selected_answer = ""

            selected_answer = str(selected_answer).strip().upper()

            correct_answer = (
                str(question.correct_answer)
                .strip()
                .upper()
            )

            is_correct = selected_answer == correct_answer

            if is_correct:
                score += 1

            # -----------------------------------
            # Save user's answer
            # -----------------------------------

            QuizAnswer.objects.create(
                quiz=quiz,
                question=question,
                selected_answer=selected_answer,
                is_correct=is_correct
            )

            # -----------------------------------
            # Prepare result
            # -----------------------------------

            results.append(
                {
                    "question_id": question.id,
                    "order": question.order,
                    "selected_answer": selected_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                }
            )

        # -----------------------------------
        # Calculate percentage
        # -----------------------------------

        total_questions = questions.count()

        percentage = round(
            (score / total_questions) * 100
        )

        # -----------------------------------
        # Update quiz
        # -----------------------------------

        quiz.score = score
        quiz.completed = True
        quiz.completed_at = timezone.now()
        quiz.save(
            update_fields=[
                "score",
                "completed",
                "completed_at"
            ]
        )

        # -----------------------------------
        # Return result
        # -----------------------------------

        return Response(
            {
                "quiz_id": quiz.id,
                "score": score,
                "total_questions": total_questions,
                "percentage": percentage,
                "completed": quiz.completed,
                "completed_at": quiz.completed_at,
                "results": results,
            },
            status=200
        )

    except Exception as e:

        print("❌ QUIZ SUBMISSION ERROR:", repr(e))
        traceback.print_exc()

        return Response(
            {
                "error": "An unexpected error occurred while submitting the quiz."
            },
            status=500
        )
        
        
        
        
        
        
        
        
@api_view(["GET"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def review_quiz_view(request, quiz_id):

    try:
        # -----------------------------------
        # Get quiz
        # -----------------------------------

        try:
            quiz = Quiz.objects.get(
                id=quiz_id,
                user=request.user
            )

        except Quiz.DoesNotExist:
            return Response(
                {
                    "error": "Quiz not found."
                },
                status=404
            )

        # -----------------------------------
        # Make sure quiz is completed
        # -----------------------------------

        if not quiz.completed:
            return Response(
                {
                    "error": "This quiz has not been completed yet."
                },
                status=400
            )

        # -----------------------------------
        # Get questions
        # -----------------------------------

        questions = quiz.questions.all().order_by("order")

        # -----------------------------------
        # Get saved answers
        # -----------------------------------

        answers = {
            answer.question_id: answer
            for answer in quiz.answers.all()
        }

        # -----------------------------------
        # Prepare review
        # -----------------------------------

        review_data = []

        for question in questions:

            answer = answers.get(question.id)

            selected_answer = ""

            if answer:
                selected_answer = answer.selected_answer

            # -----------------------------------
            # Build options
            # -----------------------------------

            options = {
                "A": question.option_a,
                "B": question.option_b,
            }

            if question.option_c:
                options["C"] = question.option_c

            if question.option_d:
                options["D"] = question.option_d

            # -----------------------------------
            # Get selected/correct option text
            # -----------------------------------

            selected_answer_text = options.get(
                selected_answer,
                ""
            )

            correct_answer_text = options.get(
                question.correct_answer,
                ""
            )

            # -----------------------------------
            # Add question review
            # -----------------------------------

            review_data.append(
                {
                    "question_id": question.id,
                    "order": question.order,
                    "question": question.question,

                    "options": options,

                    "selected_answer": selected_answer,
                    "selected_answer_text": selected_answer_text,

                    "correct_answer": question.correct_answer,
                    "correct_answer_text": correct_answer_text,

                    "explanation": question.explanation or "",

                    "is_correct": (
                        answer.is_correct
                        if answer
                        else False
                    ),
                }
            )

        # -----------------------------------
        # Calculate percentage
        # -----------------------------------

        percentage = 0

        if quiz.number_of_questions:
            percentage = round(
                (
                    quiz.score
                    / quiz.number_of_questions
                ) * 100
            )

        # -----------------------------------
        # Return review
        # -----------------------------------

        return Response(
            {
                "quiz_id": quiz.id,
                "difficulty": quiz.difficulty,
                "question_type": quiz.question_type,
                "score": quiz.score,
                "total_questions": quiz.number_of_questions,
                "percentage": percentage,
                "completed": quiz.completed,
                "completed_at": quiz.completed_at,
                "questions": review_data,
            },
            status=200
        )

    except Exception as e:

        print("❌ QUIZ REVIEW ERROR:", repr(e))
        traceback.print_exc()

        return Response(
            {
                "error": (
                    "An unexpected error occurred "
                    "while loading the quiz review."
                )
            },
            status=500
        )
        
        
@api_view(["GET"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def saved_quizzes_view(request):

    try:
        # -----------------------------------
        # Get user's quizzes
        # -----------------------------------

        quizzes = Quiz.objects.filter(
            user=request.user
        ).order_by("-created_at")

        # -----------------------------------
        # Prepare quiz list
        # -----------------------------------

        quiz_data = []

        for quiz in quizzes:

            # -------------------------------
            # Determine quiz source
            # -------------------------------

            source_type = None
            source_id = None
            source_title = None

            if quiz.lecture:
                source_type = "lecture"
                source_id = quiz.lecture.id
                source_title = (
                    re.sub(
                    r"[*#_`]",
                    "",
                    quiz.lecture.lecture
                    ).strip()[:80]
                    if quiz.lecture.lecture
                    else "Lecture"
                )             

            elif quiz.tutorial:
                source_type = "tutorial"
                source_id = quiz.tutorial.id
                source_title = (
                    quiz.tutorial.youtube_title
                    if quiz.tutorial.youtube_title
                    else "Tutorial"
                )

            # -------------------------------
            # Calculate percentage
            # -------------------------------

            percentage = 0

            if quiz.number_of_questions:
                percentage = round(
                    (
                        quiz.score
                        / quiz.number_of_questions
                    ) * 100
                )

            # -------------------------------
            # Add quiz
            # -------------------------------

            quiz_data.append(
                {
                    "id": quiz.id,
                    "source_type": source_type,
                    "source_id": source_id,
                    "source_title": source_title,
                    "difficulty": quiz.difficulty,
                    "question_type": quiz.question_type,
                    "number_of_questions": quiz.number_of_questions,
                    "score": quiz.score,
                    "percentage": percentage,
                    "completed": quiz.completed,
                    "created_at": quiz.created_at,
                    "completed_at": quiz.completed_at,
                }
            )

        # -----------------------------------
        # Return saved quizzes
        # -----------------------------------

        return Response(
            {
                "count": len(quiz_data),
                "quizzes": quiz_data,
            },
            status=200
        )

    except Exception as e:

        print("❌ SAVED QUIZZES ERROR:", repr(e))
        traceback.print_exc()

        return Response(
            {
                "error": (
                    "An unexpected error occurred "
                    "while loading saved quizzes."
                )
            },
            status=500
        )
        
        
        
        
        
        
        
        
        
        
        
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def retake_quiz_view(request, quiz_id):

    try:

        # -----------------------------------
        # Get original quiz
        # -----------------------------------

        try:

            original_quiz = Quiz.objects.get(
                id=quiz_id,
                user=request.user
            )

        except Quiz.DoesNotExist:

            return Response(
                {
                    "error": "Quiz not found."
                },
                status=404
            )


        # -----------------------------------
        # Make sure quiz has a source
        # -----------------------------------

        if not original_quiz.lecture and not original_quiz.tutorial:

            return Response(
                {
                    "error": "This quiz has no valid source."
                },
                status=400
            )


        # -----------------------------------
        # Get original source content
        # -----------------------------------

        lecture = None
        tutorial = None

        if original_quiz.lecture:

            lecture = original_quiz.lecture

            if lecture.is_deleted:

                return Response(
                    {
                        "error": "The lecture used for this quiz has been deleted."
                    },
                    status=400
                )

            source_text = lecture.lecture

            source_type = "lecture"
            source_id = lecture.id


        else:

            tutorial = original_quiz.tutorial

            if tutorial.is_deleted:

                return Response(
                    {
                        "error": "The tutorial used for this quiz has been deleted."
                    },
                    status=400
                )

            source_text = tutorial.youtube_text

            source_type = "tutorial"
            source_id = tutorial.id


        # -----------------------------------
        # Validate source content
        # -----------------------------------

        if not source_text or not source_text.strip():

            return Response(
                {
                    "error": "The original source does not contain any content."
                },
                status=400
            )


        # -----------------------------------
        # Get original quiz settings
        # -----------------------------------

        difficulty = original_quiz.difficulty

        question_type = original_quiz.question_type


        print("===================================")
        print("QUIZ RETAKE REQUEST")
        print("User:", request.user)
        print("Original Quiz ID:", original_quiz.id)
        print("Source Type:", source_type)
        print("Source ID:", source_id)
        print("Difficulty:", difficulty)
        print("Question Type:", question_type)
        print("===================================")


        # -----------------------------------
        # Generate NEW quiz
        # -----------------------------------

        print("🧠 Generating new retake quiz...")


        quiz_data = generate_quiz(
            source_text=source_text,
            difficulty=difficulty,
            question_type=question_type,
        )


        if not quiz_data:

            return Response(
                {
                    "error": "Unable to generate a new quiz. Please try again."
                },
                status=500
            )


        # -----------------------------------
        # Save NEW quiz
        # -----------------------------------

        new_quiz = save_generated_quiz(
            user=request.user,
            difficulty=difficulty,
            question_type=question_type,
            quiz_data=quiz_data,
            lecture=lecture,
            tutorial=tutorial,
        )


        if not new_quiz:

            return Response(
                {
                    "error": "Quiz was generated but could not be saved."
                },
                status=500
            )


        print(
            "✅ Quiz saved successfully. Quiz ID:",
            new_quiz.id
        )


        # -----------------------------------
        # Prepare questions
        # -----------------------------------

        questions = (
            new_quiz.questions
            .all()
            .order_by("order")
        )


        question_data = []


        for question in questions:

            options = {
                "A": question.option_a,
                "B": question.option_b,
            }


            if question.option_c:

                options["C"] = question.option_c


            if question.option_d:

                options["D"] = question.option_d


            question_data.append(
                {
                    "id": question.id,
                    "order": question.order,
                    "question": question.question,
                    "options": options,
                }
            )


        # -----------------------------------
        # Return new quiz
        # -----------------------------------

        return Response(
            {
                "id": new_quiz.id,

                "source_type": source_type,

                "source_id": source_id,

                "difficulty": new_quiz.difficulty,

                "question_type": new_quiz.question_type,

                "number_of_questions": new_quiz.number_of_questions,

                "completed": new_quiz.completed,

                "questions": question_data,
            },
            status=201
        )


    except Exception as e:

        print(
            "❌ QUIZ RETAKE ERROR:",
            repr(e)
        )

        traceback.print_exc()


        return Response(
            {
                "error": (
                    "An unexpected error occurred "
                    "while retaking the quiz."
                )
            },
            status=500
        )