from django.shortcuts import render
from .serializers import NoteSerializer, ContactSerializer, TaskSerializer, LectureSerializer, TutorialSerializer, SubscriptionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Note, Contact, Tutorial, Subscription
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer
from django.db.models import Q
from datetime import datetime
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
            model="llama-3.1-8b-instant",
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
        
        # threading.Thread(
        #     target=process_audio,
        #     args=(lecture.id,)
        # ).start()
        
        process_audio(lecture.id)
        
       
        
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
        short_text = transcript.text[:3000]
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
        prompt = f"Convert this into structured lecture notes:\n{transcription[:3000]}"
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1200,
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
@permission_classes([IsAuthenticated])
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
                    model="llama-3.1-8b-instant",
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
        "metadata": {
            "user_id": request.user.id,
            "plan": plan_name,
        },
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
    try:
        subscription = request.user.subscription
    except Subscription.DoesNotExist:
        return Response(
            {"detail": "Subscription not found."},
            status=404
        )

    if subscription.paystack_reference != reference:
        return Response(
            {"detail": "Invalid payment reference."},
            status=400
        )

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers,
            timeout=30,
        )

        response_data = response.json()

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
                    "Payment verification failed."
                )
            },
            status=400
        )

    transaction = response_data.get("data", {})

    if transaction.get("status") != "success":
        return Response(
            {
                "detail": "Payment was not successful.",
                "status": transaction.get("status"),
            },
            status=400
        )
        
    try:
       activate_subscription(subscription, transaction)

    except ValueError as e:
        return Response(
        {"detail": str(e)},
        status=400
        )

   

    return Response(
        {
            "message": "Payment verified successfully.",
            "plan": subscription.plan,
            "status": subscription.status,
            "subscription_start": subscription.subscription_start,
            "subscription_end": subscription.subscription_end,
        }
    )
    
    
    
def activate_subscription(subscription, transaction):
    
    plan = subscription.plan
    
    now = timezone.now()
    
    if plan == "monthly":
        subscription_end = now + timedelta(days=30)
    
    elif plan == "yearly":
        subscription_end = now + timedelta(days=365)
    
    else:
        return Response(
           {"detail": "Invalid subscription plan."},
            status=400
        )
    
    subscription.status = "active"
    subscription.subscription_start = now
    subscription.subscription_end = subscription_end
    
    subscription.paystack_transaction_id = str(
        transaction.get("id")
    )
    
   
    
    transaction_id = transaction.get("id")

    if transaction_id:
        subscription.paystack_transaction_id = str(transaction_id)

    subscription.save()

    return subscription




@api_view(["POST"])
def paystack_webhook(request):
    
    print("PAYSTACK WEBHOOK RECEIVED")
    print("BODY:", request.body)
    print("SIGNATURE:", request.headers.get("x-paystack-signature"))

    signature = request.headers.get("x-paystack-signature")

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

    if event.get("event") != "charge.success":
        return Response(
            {"message": "Event ignored."},
            status=200
        )

    transaction = event.get("data", {})

    reference = transaction.get("reference")

    if not reference:
        return Response(
            {"detail": "Missing transaction reference."},
            status=400
        )

    try:
        subscription = Subscription.objects.get(
            paystack_reference=reference
        )

    except Subscription.DoesNotExist:
        return Response(
            {"detail": "Subscription not found."},
            status=404
        )

    if subscription.status == "active":
        return Response(
            {"message": "Subscription already active."},
            status=200
        )

    try:
        activate_subscription(
            subscription,
            transaction
        )

    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=400
        )

    return Response(
        {"message": "Payment processed successfully."},
        status=200
    )