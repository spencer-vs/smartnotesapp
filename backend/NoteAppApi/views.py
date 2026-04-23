from django.shortcuts import render
from .serializers import NoteSerializer, ContactSerializer, TaskSerializer, LectureSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Note, Contact, Tutorial
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from django.db.models import Q
from datetime import datetime
import time
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

# Create your views here.

User = get_user_model()

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
    
    
    



# def generate_lecture_note(transcription):
#     try:
#         api_key = os.getenv("GROQ_API_KEY")
#         if not api_key:
#             print("Groq API key not found")
#             return None
#         print("Grok key found sending request...")
#         client = Groq(api_key=api_key)
#         prompt = f"""
#         You are an expert academic assistant.
#         Convert the following transcript into well-structured lecture notes.
#         REQUIREMENTS:
#         - Use clear headings and subheadings
#         - Use bullet points where appropriate
#         - Highlight key concepts
#         - Keep it concise but complete
#         - Add a short summary at the end
#         Transcript:
#         {transcription}
#         Lecture Notes:
#         """
#         completion = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "user", "content": prompt[:3000]},
#             ],
#             temperature=0.5,   # lower = more structured
#             max_tokens=1200,
#             timeout=60
#         )
#         print("Grok response received")
#         return completion.choices[0].message.content.strip()
#     except Exception as e:
#         print("Groq error:", repr(e))
#         return None
    
    
    
    
    

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
            return JsonResponse({'error': 'Failed to generate blog'}, status=500)
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
                [item["text"] for item in transcript_list]
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
        Based on the generated transcript, create lecture notes, covering all relevant aspects of the video.
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