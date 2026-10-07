from django.shortcuts import render
from .serializers import NoteSerializer, ContactSerializer, TaskSerializer, LectureSerializer, TutorialSerializer, SubscriptionSerializer, TaskItemSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Note, Contact, Tutorial, Subscription,  Quiz, QuizQuestion, QuizAnswer, Task, TaskItem
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer
from django.db.models import Q
import time
from datetime import timedelta
from datetime import time as datetime_time
from .quiz_generator import generate_quiz, save_generated_quiz
from django.db import transaction
from openai import OpenAI
from django.http import JsonResponse
import json
import os
import re
import requests
from langdetect import detect
from groq import Groq, RateLimitError
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
            f"https://smartnotes.cv/auth/reset-password/"
            f"{uidb64}/{token}"
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


# def send_reset_email(to_email, reset_link):
#     resend.Emails.send({
#         "from": settings.FROM_EMAIL,
#         "to": [to_email],
#         "subject": "Password Reset",
#         "html": f"""
#         <h2>Password Reset</h2>
#         <p>Click the link below to reset your password</p>
#         <a href="{reset_link}">{reset_link}</a>"""
#     })

resend.api_key = settings.RESEND_API_KEY

def send_reset_email(to_email, reset_link):
    resend.Emails.send({
        "from": settings.FROM_EMAIL,
        "to": [to_email],
        "subject": "Reset Your SmartNotes Password",
        "html": f"""
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 30px;
            background-color: #f7f7f7;
        ">
            <div style="
                background-color: #00030E;
                padding: 30px;
                border-radius: 12px;
                text-align: center;
            ">
                <h2 style="
                    color: #FFB300;
                    margin-bottom: 10px;
                ">
                    SmartNotes
                </h2>

                <p style="
                    color: #FFFFFF;
                    font-size: 16px;
                ">
                    Password Reset
                </p>

                <p style="
                    color: #CCCCCC;
                    font-size: 14px;
                    line-height: 1.6;
                ">
                    We received a request to reset your SmartNotes
                    password. Tap the button below to create a new password.
                </p>

                <a
                    href="{reset_link}"
                    style="
                        display: inline-block;
                        background-color: #FFB300;
                        color: #00030E;
                        padding: 14px 24px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-weight: bold;
                        font-size: 14px;
                        margin-top: 15px;
                    "
                >
                    Reset Password
                </a>

                <p style="
                    color: #777980;
                    font-size: 12px;
                    line-height: 1.5;
                    margin-top: 25px;
                ">
                    If you did not request a password reset, you can safely
                    ignore this email.
                </p>
            </div>
        </div>
        """
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
        date_obj = datetime_time.strptime(query, "%Y-%m-%d").date()
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
                date_obj = datetime_time.strptime(query, "%Y-%m-%d").date()
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
    


# ============================================================
# CREATE TASK
# ============================================================

# ============================================================
# CREATE TASK
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def create_task(request):

    try:
        title = request.data.get("title")
        items = request.data.get("items")

        # ----------------------------------------------------
        # Validate title
        # ----------------------------------------------------

        if not isinstance(title, str) or not title.strip():
            return JsonResponse(
                {"error": "Task title is required."},
                status=400
            )

        title = title.strip()

        if len(title) > 150:
            return JsonResponse(
                {
                    "error": "Task title cannot exceed 150 characters."
                },
                status=400
            )

        # ----------------------------------------------------
        # Validate items
        # ----------------------------------------------------

        if not isinstance(items, list):
            return JsonResponse(
                {
                    "error": "Task items must be provided as a list."
                },
                status=400
            )

        if len(items) < 2:
            return JsonResponse(
                {
                    "error": "At least 2 task items are required."
                },
                status=400
            )

        # ----------------------------------------------------
        # Clean and validate individual items
        # ----------------------------------------------------

        cleaned_items = []

        for item in items:

            if not isinstance(item, str):
                return JsonResponse(
                    {
                        "error": "Every task item must be text."
                    },
                    status=400
                )

            item = item.strip()

            if item:
                cleaned_items.append(item)

        # ----------------------------------------------------
        # Minimum valid items
        # ----------------------------------------------------

        if len(cleaned_items) < 2:
            return JsonResponse(
                {
                    "error": "At least 2 valid task items are required."
                },
                status=400
            )

        # ----------------------------------------------------
        # Maximum items
        #
        # Monday-Saturday = 6 days
        # Maximum 2 items per day
        # 6 × 2 = 12 items maximum
        # ----------------------------------------------------

        if len(cleaned_items) > 12:
            return JsonResponse(
                {
                    "error": (
                        "A weekly task can contain a maximum "
                        "of 12 items."
                    )
                },
                status=400
            )

        # ----------------------------------------------------
        # Check if user already has an active task
        # ----------------------------------------------------

        active_task_exists = Task.objects.filter(
            user=request.user,
            is_deleted=False,
            completed=False
        ).exists()

        if active_task_exists:
            return JsonResponse(
                {
                    "error": (
                        "You already have an active task. "
                        "Complete or delete it before "
                        "creating a new one."
                    )
                },
                status=400
            )

        # ----------------------------------------------------
        # Calculate next Monday
        # ----------------------------------------------------

        today = timezone.localdate()

        days_until_monday = (7 - today.weekday()) % 7

        week_start = today + timedelta(
            days=days_until_monday
        )

        # Monday + 5 days = Saturday
        week_end = week_start + timedelta(days=5)

        # ----------------------------------------------------
        # Ask Groq to organize the user's items
        # ----------------------------------------------------

        schedule = generate_task_schedule(cleaned_items)

        if not schedule:
            return JsonResponse(
                {
                    "error": (
                        "Could not generate a task schedule. "
                        "Please try again."
                    )
                },
                status=500
            )

        # ----------------------------------------------------
        # Validate Groq response
        # ----------------------------------------------------

        validation_error = validate_task_schedule(
            schedule,
            len(cleaned_items)
        )

        if validation_error:
            print(
                "❌ Schedule validation failed:",
                validation_error
            )

            return JsonResponse(
                {
                    "error": "Generated schedule was invalid.",
                    "details": validation_error
                },
                status=500
            )

        # ----------------------------------------------------
        # Valid day offsets
        # ----------------------------------------------------

        day_offsets = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
        }

        # ----------------------------------------------------
        # Create Task + TaskItems atomically
        # ----------------------------------------------------

        with transaction.atomic():

            task = Task.objects.create(
                user=request.user,
                todo_title=title,
                week_start=week_start,
                week_end=week_end,
                completed=False,
                is_deleted=False
            )

            # Track order separately from the user's
            # original item index.
            item_order = 1

            for scheduled_item in schedule:

                item_index = scheduled_item["item_index"]
                day_name = scheduled_item["day"]

                # ------------------------------------------------
                # Get the original user-provided description
                # ------------------------------------------------

                description = cleaned_items[item_index - 1]

                # ------------------------------------------------
                # Calculate the actual date
                # ------------------------------------------------

                item_date = week_start + timedelta(
                    days=day_offsets[day_name]
                )

                # ------------------------------------------------
                # Django determines the time slot.
                #
                # First item of the day:
                # 08:00 - 10:00
                #
                # Second item:
                # 11:00 - 13:00
                # ------------------------------------------------

                existing_items_today = TaskItem.objects.filter(
                    task=task,
                    date=item_date
                ).count()

                if existing_items_today == 0:

                    start_time = time(8, 0)
                    end_time = time(10, 0)

                elif existing_items_today == 1:

                    start_time = time(11, 0)
                    end_time = time(13, 0)

                else:

                    raise ValueError(
                        f"More than 2 items scheduled on {day_name}."
                    )

                # ------------------------------------------------
                # Create TaskItem
                # ------------------------------------------------

                TaskItem.objects.create(
                    task=task,
                    description=description,
                    date=item_date,
                    start_time=start_time,
                    end_time=end_time,
                    completed=False,
                    order=item_order
                )

                item_order += 1

        # ----------------------------------------------------
        # Return complete task
        # ----------------------------------------------------

        task.refresh_from_db()

        serializer = TaskSerializer(task)

        return JsonResponse(
            serializer.data,
            status=201
        )

    except Exception as e:

        print("❌ CREATE TASK ERROR:")
        traceback.print_exc()

        return JsonResponse(
            {
                "error": "Server error.",
                "details": str(e)
            },
            status=500
        )
# ============================================================
# GROQ TASK SCHEDULER
# ============================================================

# ============================================================
# GROQ TASK SCHEDULER
# ============================================================

def generate_task_schedule(user_items):

    try:

        api_key = os.getenv("GROQ_API_KEY")

        if api_key:
            api_key = api_key.strip()

        if not api_key:
            print("❌ Groq API key not found")
            return None

        client = Groq(api_key=api_key)

        # ----------------------------------------------------
        # Number the user's items so Groq can reference them
        # ----------------------------------------------------

        numbered_items = "\n".join(
            f"{index}. {item}"
            for index, item in enumerate(user_items, start=1)
        )

        # ----------------------------------------------------
        # Scheduling prompt
        # ----------------------------------------------------

        prompt = f"""
You are a weekly task scheduling assistant.

The user has provided these task items:

{numbered_items}

Your ONLY job is to assign each item to a day from Monday
through Saturday.

IMPORTANT RULES:

1. You MUST use every item exactly once.
2. You MUST NOT create new items.
3. You MUST NOT remove any item.
4. You MUST NOT rewrite any item.
5. You MUST NOT summarize any item.
6. You MUST NOT combine any items.
7. You MUST NOT split any items.
8. Use Monday through Saturday only.
9. NEVER use Sunday.
10. Maximum 2 items may be assigned to the same day.
11. You MUST schedule all {len(user_items)} items.
12. The "item_index" must refer to the original item number.
13. Do not change the item_index.
14. Return ONLY valid JSON.
15. Do not return Markdown.
16. Do not include explanations.

Return exactly this structure:

{{
    "items": [
        {{
            "item_index": 1,
            "day": "Monday"
        }},
        {{
            "item_index": 2,
            "day": "Tuesday"
        }}
    ]
}}

Remember:

- Every item must appear exactly once.
- Every item_index must be between 1 and {len(user_items)}.
- Maximum 2 items per day.
- Sunday is forbidden.
"""

        # ----------------------------------------------------
        # Ask Groq for the schedule
        # ----------------------------------------------------

        completion = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict weekly task scheduling "
                        "assistant. Return JSON only. "
                        "Never write explanations or Markdown. "
                        "Never modify the user's task items."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        # ----------------------------------------------------
        # Get Groq response
        # ----------------------------------------------------

        response_text = (
            completion
            .choices[0]
            .message
            .content
            .strip()
        )

        print("🤖 GROQ RESPONSE:")
        print(response_text)

        # ----------------------------------------------------
        # Remove accidental Markdown code fences
        # ----------------------------------------------------

        if response_text.startswith("```"):

            response_text = response_text.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        schedule_data = json.loads(response_text)

        # ----------------------------------------------------
        # Validate expected top-level structure
        # ----------------------------------------------------

        if not isinstance(schedule_data, dict):
            print("❌ Groq response is not a JSON object")
            return None

        schedule = schedule_data.get("items")

        if not isinstance(schedule, list):
            print("❌ Groq response does not contain an items list")
            return None

        return schedule

    except json.JSONDecodeError:

        print("❌ Groq returned invalid JSON")
        traceback.print_exc()

        return None

    except Exception:

        print("❌ Groq scheduling error:")
        traceback.print_exc()

        return None

# ============================================================
# VALIDATE GROQ SCHEDULE
# ============================================================

# ============================================================
# VALIDATE GROQ SCHEDULE
# ============================================================

def validate_task_schedule(schedule, total_items):

    # --------------------------------------------------------
    # Basic structure
    # --------------------------------------------------------

    if not isinstance(schedule, list):
        return "Schedule must be a list."

    if len(schedule) != total_items:
        return (
            f"Expected {total_items} scheduled items, "
            f"but received {len(schedule)}."
        )

    # --------------------------------------------------------
    # Valid days
    # --------------------------------------------------------

    valid_days = {
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    }

    # --------------------------------------------------------
    # Expected item indexes
    # --------------------------------------------------------

    expected_indexes = set(
        range(1, total_items + 1)
    )

    received_indexes = []

    daily_counts = {}

    # --------------------------------------------------------
    # Validate each scheduled item
    # --------------------------------------------------------

    for item in schedule:

        # ----------------------------------------------------
        # Each schedule entry must be an object
        # ----------------------------------------------------

        if not isinstance(item, dict):
            return "Each scheduled item must be an object."

        # ----------------------------------------------------
        # item_index
        # ----------------------------------------------------

        if "item_index" not in item:
            return "Missing item_index."

        item_index = item["item_index"]

        if not isinstance(item_index, int):
            return "item_index must be an integer."

        if item_index not in expected_indexes:
            return (
                f"Invalid item_index: {item_index}. "
                f"Expected values between 1 and {total_items}."
            )

        received_indexes.append(item_index)

        # ----------------------------------------------------
        # Day
        # ----------------------------------------------------

        if "day" not in item:
            return (
                f"Missing day for item {item_index}."
            )

        day = item["day"]

        if not isinstance(day, str):
            return (
                f"Day must be text for item {item_index}."
            )

        if day not in valid_days:
            return f"Invalid day: {day}"

        # ----------------------------------------------------
        # Count items per day
        # ----------------------------------------------------

        daily_counts[day] = (
            daily_counts.get(day, 0) + 1
        )

        # ----------------------------------------------------
        # Maximum 2 items per day
        # ----------------------------------------------------

        if daily_counts[day] > 2:
            return (
                f"More than 2 items scheduled on {day}."
            )

    # --------------------------------------------------------
    # Make sure every item appears exactly once
    # --------------------------------------------------------

    if len(received_indexes) != len(set(received_indexes)):
        return "An item was scheduled more than once."

    received_indexes_set = set(received_indexes)

    if received_indexes_set != expected_indexes:
        missing_indexes = (
            expected_indexes - received_indexes_set
        )

        extra_indexes = (
            received_indexes_set - expected_indexes
        )

        if missing_indexes:
            return (
                "Some user-provided items were missing: "
                f"{sorted(missing_indexes)}."
            )

        if extra_indexes:
            return (
                "Invalid item indexes were returned: "
                f"{sorted(extra_indexes)}."
            )

        return "Scheduled items do not match the user's items."

    # --------------------------------------------------------
    # Final capacity check
    #
    # Monday-Saturday = 6 days
    # Maximum 2 items/day = 12 items
    # --------------------------------------------------------

    if total_items > 12:
        return (
            "Too many items for the Monday-Saturday schedule. "
            "Maximum is 12 items."
        )

    # --------------------------------------------------------
    # Schedule is valid
    # --------------------------------------------------------

    return None

# ============================================================
# GET SINGLE TASK
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_task(request):
    task = Task.objects.filter(
        user=request.user,
        is_deleted=False,
        completed=False
    ).prefetch_related('items').first()

    if not task:
        return Response(
            {"detail": "No active task found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TaskSerializer(task)

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request, id):

    try:

        task = Task.objects.get(
            id=id,
            user=request.user,
            is_deleted=False
        )

        serializer = TaskSerializer(task)

        return JsonResponse(
            serializer.data,
            status=200
        )

    except Task.DoesNotExist:

        return JsonResponse(
            {"error": "Task not found"},
            status=404
        )

    except Exception:

        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error"},
            status=500
        )


# ============================================================
# GET ALL TASKS
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_task(request):

    try:

        tasks = Task.objects.filter(
            user=request.user,
            is_deleted=False
        ).order_by('-created_at')

        data = []

        for task in tasks:

            total_items = task.items.count()

            completed_items = task.items.filter(
                completed=True
            ).count()

            data.append({
                "id": task.id,
                "todo_title": task.todo_title,
                "week_start": task.week_start,
                "week_end": task.week_end,
                "completed": task.completed,
                "total_items": total_items,
                "completed_items": completed_items,
                "created_at": task.created_at,
            })

        return JsonResponse(
            data,
            safe=False,
            status=200
        )

    except Exception:

        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error"},
            status=500
        )


# ============================================================
# COMPLETE / UNCOMPLETE TASK ITEM
# ============================================================

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_item(request, task_id, item_id):

    try:

        task = Task.objects.get(
            id=task_id,
            user=request.user,
            is_deleted=False
        )

        item = TaskItem.objects.get(
            id=item_id,
            task=task
        )

        completed = request.data.get("completed")

        if not isinstance(completed, bool):
            return JsonResponse(
                {
                    "error": (
                        "completed must be either true or false."
                    )
                },
                status=400
            )

        item.completed = completed
        item.save(update_fields=["completed"])

        # ----------------------------------------------------
        # Task is completed only when ALL items are completed
        # ----------------------------------------------------

        all_items_completed = not task.items.filter(
            completed=False
        ).exists()

        task.completed = all_items_completed

        task.save(update_fields=["completed"])

        return JsonResponse(
            {
                "message": "Task item updated successfully.",
                "item": TaskItemSerializer(item).data,
                "task_completed": task.completed,
            },
            status=200
        )

    except Task.DoesNotExist:

        return JsonResponse(
            {"error": "Task not found"},
            status=404
        )

    except TaskItem.DoesNotExist:

        return JsonResponse(
            {"error": "Task item not found"},
            status=404
        )

    except Exception:

        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error"},
            status=500
        )


# ============================================================
# DELETE TASK - SOFT DELETE
# ============================================================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_task(request, id):

    try:

        task = Task.objects.get(
            id=id,
            user=request.user,
            is_deleted=False
        )

        task.is_deleted = True
        task.save(update_fields=["is_deleted"])

        return JsonResponse(
            {
                "message": "Task deleted successfully."
            },
            status=200
        )

    except Task.DoesNotExist:

        return JsonResponse(
            {"error": "Task not found"},
            status=404
        )

    except Exception:

        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error"},
            status=500
        )
        
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lecture_detail(request, id):
    try:
        lecture = Lecture.objects.get(id=id, user=request.user, is_deleted=False)
        return JsonResponse({
            "id": lecture.id,
            "title": lecture.title,
            "lecture": lecture.lecture,
            "transcript": lecture.transcript,
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
                "transcript": lecture.transcript,
                "created_at": lecture.created_at
            }
            for lecture in lectures
        ]
        return JsonResponse(data, safe=False)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error'}, status=500)




# @csrf_exempt
# @api_view(['POST'])
# @permission_classes([IsAuthenticated, HasPremiumSubscription])
# def upload_audio(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=405)
#     try:
#         print("USER:", request.user)
#         print("AUTH:", request.user.is_authenticated)
#         audio_file = request.FILES.get("audio")
#         title = request.data.get("title", "").strip()
#         if not audio_file:
#             return JsonResponse({"error": "No audio file"}, status=400)
#         MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50 MB

#         if audio_file.size > MAX_AUDIO_SIZE:
#              return JsonResponse(
#             {
#             "error": "Audio file is too large. "
#                      "Maximum allowed size is 50 MB."
#             }, status=400)
#         folder = os.path.join(settings.MEDIA_ROOT, "audio")
#         os.makedirs(folder, exist_ok=True)
      
#         lecture = Lecture.objects.create(
#            user=request.user,
#            title=title,
#            audio_file=audio_file,
#            status="processing"
#        )
        
        
#         process_audio(lecture.id)
        
       
        
#         return JsonResponse(
#             {
#                 "message": "Processing started",
#                 "lecture_id": lecture.id,
#                 "title": lecture.title,
#             }, status=202
#         )
#     except Exception as e:
#         print("UPLOAD ERROR:", str(e))
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)



# def process_audio(lecture_id):
#     try:
#         lecture = Lecture.objects.get(id=lecture_id)
#         file_path = lecture.audio_file.path
        
#         api_key = os.getenv("ASSEMBLYAI_API_KEY")
#         if not api_key:
#             print("AssemblyAI key missing!")
#             lecture.status = "failed"
#             lecture.save()
#             return
#         aai.settings.api_key = api_key
#         transcriber = aai.Transcriber()
#         config = aai.TranscriptionConfig(speech_models=["universal-3-pro", "universal-2"])
#         transcript = transcriber.transcribe(lecture.audio_file.path, config=config)
       
#         # print("FULL TRANSCRIPT:", transcript.text)
#         if transcript.status == "error":
#             print("AssemblyAI error:", transcript.error)
#             lecture.status = "failed"
#             lecture.save()
#             return
#         transcript_text = transcript.text or ""

#         lecture.transcript = transcript_text
#         lecture.save(update_fields=["transcript"])
#         notes = generate_lecture_note(transcript_text)
        
#         if not notes:
#             print("Grok failed, no notes generated")
#             lecture.status= "failed"
#             lecture.save(update_fields=["status"])
#             return
    
#         lecture.transcript = transcript_text
#         lecture.lecture = notes
#         lecture.status = "completed"
        
#         lecture.save(
#             update_fields=[
#             "transcript",
#             "lecture",
#             "status",
#         ]
#         )

       
        
#         if os.path.exists(file_path):
#             os.remove(file_path)
#             print('Audio file deleted successfully')
            
#     except Exception as e:
#         print("Audio processing error:", str(e))
#         traceback.print_exc()
#         try:
#             lecture = Lecture.objects.get(id=lecture_id)
#             lecture.status = "failed"
#             lecture.save()
#         except:
#             pass
        
    
    
    

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def upload_audio(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Invalid request"},
            status=405
        )

    try:

        print("USER:", request.user)
        print("AUTH:", request.user.is_authenticated)

        # -----------------------------------
        # Get uploaded audio
        # -----------------------------------

        audio_file = request.FILES.get("audio")

        title = request.data.get(
            "title",
            ""
        ).strip()


        # -----------------------------------
        # Validate audio
        # -----------------------------------

        if not audio_file:

            return JsonResponse(
                {
                    "error": "No audio file"
                },
                status=400
            )


        # -----------------------------------
        # Maximum audio size
        # -----------------------------------

        MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50 MB

        if audio_file.size > MAX_AUDIO_SIZE:

            return JsonResponse(
                {
                    "error": (
                        "Audio file is too large. "
                        "Maximum allowed size is 50 MB."
                    )
                },
                status=400
            )


        # -----------------------------------
        # Create Lecture record
        # -----------------------------------

        lecture = Lecture.objects.create(

            user=request.user,

            title=title,

            audio_file=audio_file,

            status="processing"

        )


        print(
            f"🎧 Audio upload saved. "
            f"Lecture ID: {lecture.id}"
        )


        # -----------------------------------
        # Process audio
        # -----------------------------------

        process_audio(lecture.id)


        # -----------------------------------
        # Response
        # -----------------------------------

        return JsonResponse(
            {
                "message": "Processing started",

                "lecture_id": lecture.id,

                "title": lecture.title,
            },
            status=202
        )


    except Exception as e:

        print(
            "❌ UPLOAD ERROR:",
            str(e)
        )

        traceback.print_exc()

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )
        
        


def process_audio(lecture_id):

    file_path = None

    try:

        # -----------------------------------
        # Get lecture
        # -----------------------------------

        lecture = Lecture.objects.get(
            id=lecture_id
        )


        file_path = lecture.audio_file.path


        print(
            f"🎧 Starting audio processing "
            f"for Lecture {lecture_id}"
        )


        # -----------------------------------
        # Get Groq API key
        # -----------------------------------

        api_key = os.getenv(
            "GROQ_API_KEY",
            ""
        ).strip()


        if not api_key:

            print(
                "❌ GROQ_API_KEY is missing"
            )

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

            return


        # -----------------------------------
        # Verify audio file exists
        # -----------------------------------

        if not os.path.exists(file_path):

            print(
                "❌ Audio file does not exist:",
                file_path
            )

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

            return


        # -----------------------------------
        # Create Groq client
        # -----------------------------------

        client = Groq(
            api_key=api_key,
            max_retries=0
        )


        # -----------------------------------
        # Transcribe audio with Whisper
        # -----------------------------------

        print(
            "🎙️ Transcribing audio with "
            "Whisper Large V3 Turbo..."
        )


        with open(
            file_path,
            "rb"
        ) as audio:

            transcription = (
                client.audio.transcriptions.create(

                    file=audio,

                    model="whisper-large-v3-turbo",

                    response_format="json",

                    temperature=0.0,

                )
            )


        # -----------------------------------
        # Get transcript text
        # -----------------------------------

        transcript_text = (
            transcription.text or ""
        ).strip()


        if not transcript_text:

            print(
                "❌ Groq returned an empty transcript"
            )

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

            return


        print(
            "✅ Audio transcription completed"
        )

        print(
            "Transcript length:",
            len(transcript_text),
            "characters"
        )


        # -----------------------------------
        # Save transcript
        # -----------------------------------

        lecture.transcript = transcript_text

        lecture.save(
            update_fields=["transcript"]
        )


        # -----------------------------------
        # Generate lecture notes
        # -----------------------------------

        print(
            "🧠 Generating lecture notes..."
        )


        notes = generate_lecture_note(
            transcript_text
        )


        if not notes:

            print(
                "❌ Lecture-note generation failed"
            )

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

            return


        # -----------------------------------
        # Save final result
        # -----------------------------------

        lecture.lecture = notes

        lecture.status = "completed"

        lecture.save(
            update_fields=[
                "lecture",
                "status",
            ]
        )


        print(
            f"✅ Audio processing completed "
            f"for Lecture {lecture_id}"
        )


        # -----------------------------------
        # Delete original audio file
        # -----------------------------------

        if os.path.exists(file_path):

            os.remove(file_path)

            print(
                "🗑️ Audio file deleted successfully"
            )


    except Exception as e:

        print(
            "❌ Audio processing error:",
            repr(e)
        )

        traceback.print_exc()


        # -----------------------------------
        # Mark lecture as failed
        # -----------------------------------

        try:

            lecture = Lecture.objects.get(
                id=lecture_id
            )

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

        except Exception:

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
    """
    Generate detailed lecture notes from an audio transcript
    using Groq GPT-OSS 20B.

    The complete transcript is sent in one request.
    No manual transcript truncation or chunking is performed.
    """

    try:

        # -----------------------------------
        # Validate transcript
        # -----------------------------------

        if not transcription or not transcription.strip():

            print(
                "❌ No transcript provided "
                "for lecture-note generation"
            )

            return None

        # -----------------------------------
        # Get Groq API key
        # -----------------------------------

        api_key = os.getenv(
            "GROQ_API_KEY",
            ""
        ).strip()

        if not api_key:

            print(
                "❌ GROQ_API_KEY is missing"
            )

            return None

        # -----------------------------------
        # Groq client
        # -----------------------------------

        client = Groq(
            api_key=api_key,
            max_retries=0
        )

        # -----------------------------------
        # Lecture-note prompt
        # -----------------------------------

        prompt = f"""
You are the SmartNotes Lecture Notes Generator.

Based on the transcript below, create clear, detailed,
well-structured lecture notes that a student can use
for studying.

The notes should allow a student to understand and study
the lecture without needing to listen to the original
recording again.

IMPORTANT REQUIREMENTS:

1. Cover all important topics and information contained
   in the entire transcript.

2. Do not produce a simple summary.

3. Explain concepts clearly and in enough depth for a
   student to learn from the notes.

4. Preserve important:
   - definitions
   - explanations
   - examples
   - processes
   - comparisons
   - names
   - dates
   - places
   - numbers
   - terminology
   - technical information

5. Do not invent information that is not supported by
   the transcript.

6. Do not introduce unrelated outside information.

7. Organize the lecture notes into meaningful sections.

8. Use clear headings and subheadings where appropriate.

9. Use paragraphs, bullet points, and numbered lists when
   they improve readability.

10. When the lecture contains a comparison between two
    or more concepts, present the comparison using a
    simple readable structure.

11. Do not use Markdown table syntax.

12. Do not use characters such as:
    |
    ---
    to create tables.

13. Instead, use clearly labelled comparison sections.

Example:

Comparison: Type A vs Type B

Feature: Speed
Type A: Fast
Type B: Slow

Feature: Cost
Type A: High
Type B: Low

14. Keep technical terms, programming keywords, commands,
    and code examples accurate.

15. Use backticks for short technical syntax where
    appropriate.

16. Avoid unnecessary repetition.

17. Maintain a logical flow from the beginning of the
    lecture to the end.

18. Correct obvious transcription errors when the intended
    meaning is clear.

19. Do not mention that the content came from a transcript.

20. End the lecture notes with a concise conclusion that
    brings together the main concepts covered.

21. Where appropriate, include a short "Further Reading"
    section based ONLY on topics actually discussed in
    the lecture.

22. Do not invent books, websites, authors, or sources
    for the Further Reading section.

IMPORTANT:

The transcript may contain spoken-language repetition,
informal expressions, incomplete sentences, or minor
transcription errors.

Clean these up where necessary while preserving the
lecturer's intended meaning.

Return only the completed lecture notes.

TRANSCRIPT:

{transcription}

LECTURE NOTES:
"""

        # -----------------------------------
        # Generate lecture notes
        # -----------------------------------

        max_attempts = 2

        for attempt in range(
            1,
            max_attempts + 1
        ):

            try:

                completion = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.5,

                    max_tokens=16000,
                )

                lecture_notes = (
                    completion
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

                # -----------------------------------
                # Track actual token usage
                # -----------------------------------

                if completion.usage:

                    print(
                        "Lecture-note generation usage:"
                    )

                    print(
                        "Input tokens:",
                        completion.usage.prompt_tokens
                    )

                    print(
                        "Output tokens:",
                        completion.usage.completion_tokens
                    )

                    print(
                        "Total tokens:",
                        completion.usage.total_tokens
                    )

                # -----------------------------------
                # Validate response
                # -----------------------------------

                if lecture_notes:

                    print(
                        "✅ Lecture notes generated "
                        "successfully"
                    )

                    return lecture_notes

                print(
                    f"⚠️ Lecture-note generation attempt "
                    f"{attempt} returned empty content"
                )

            except Exception as e:

                print(
                    f"❌ Lecture-note generation attempt "
                    f"{attempt} failed:",
                    repr(e)
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying lecture-note generation..."
                    )

                    time.sleep(2)

        # -----------------------------------
        # All attempts failed
        # -----------------------------------

        print(
            "❌ Lecture-note generation failed "
            "after all attempts"
        )

        return None

    except Exception as e:

        print(
            "❌ Lecture-note generation fatal error:",
            repr(e)
        )

        traceback.print_exc()

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
            "transcript": tutorial.transcript,
            "video_link": tutorial.youtube_link,
            "created_at": tutorial.created_at
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
                "text": tutorial.youtube_text,
                "created_at": tutorial.created_at
            }
            for tutorial in tutorials
        ]
        return JsonResponse(data, safe=False)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error'}, status=500)


 
 
 
 
 
# @api_view(["POST"])
# @permission_classes([IsAuthenticated, HasPremiumSubscription])
# def generate_tutorial(request):
  
#     if request.method != "POST":
#         return JsonResponse({'error': 'Invalid request method'}, status=405)
#     try:
       
#         yt_link = request.data.get('link')
#         if not yt_link:
#             return JsonResponse({'error': 'No YouTube link provided'}, status=400)
       
#         # Extract video ID
#         video_id = get_video_id(yt_link)
        
       
#         if not video_id:
#             return JsonResponse({'error': 'Invalid YouTube URL'}, status=400)
#         title = get_youtube_title(video_id)
#         # Get transcript
#         # transcription = transcription[:1200]
#         transcription = get_transcription(video_id)
#         if not transcription:
#             return JsonResponse(
#             {
#             'error': (
#                 'A transcript could not be retrieved for this YouTube video. '
#                 'Please try another video.'
#             )
#             },
#         status=400
#     )
#         # Translate transcript to English
        
#         english_transcription = translate_transcript_to_english(transcription)

#         if not english_transcription:
#            return JsonResponse(
#            {'error': 'Failed to translate transcript to English'},
#            status=500
#            )

#         # Generate blog
#         tutorial = generate_tutorial_from_transcript(english_transcription)
#         if not tutorial:
#             return JsonResponse({'error': 'Failed to generate tutorial'}, status=500)
#         # Save blog to database
#         new_tutorial = Tutorial.objects.create(
#             user=request.user,
#             youtube_title=title,
#             youtube_link=yt_link,
#             youtube_text=tutorial,
#             transcript=english_transcription
#         )
#         new_tutorial.save()
        
        
        
#         return JsonResponse({'content': tutorial})
#     except Exception as e:
#         print("SERVER ERROR:", e)
#         return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)





@api_view(["POST"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def generate_tutorial(request):

    if request.method != "POST":
        return JsonResponse(
            {'error': 'Invalid request method'},
            status=405
        )

    try:

        yt_link = request.data.get('link')

        if not yt_link:
            return JsonResponse(
                {'error': 'No YouTube link provided'},
                status=400
            )

        # -----------------------------------
        # Extract video ID
        # -----------------------------------

        video_id = get_video_id(yt_link)

        if not video_id:
            return JsonResponse(
                {'error': 'Invalid YouTube URL'},
                status=400
            )

        # -----------------------------------
        # Get YouTube title
        # -----------------------------------

        title = get_youtube_title(video_id)

        # -----------------------------------
        # Get transcript
        # -----------------------------------

        transcription = get_transcription(video_id)

        if not transcription:
            return JsonResponse(
                {
                    'error': (
                        'A transcript could not be retrieved for '
                        'this YouTube video. Please try another video.'
                    )
                },
                status=400
            )

        # -----------------------------------
        # Detect transcript language
        # -----------------------------------

        try:

            detected_language = detect(
                transcription
            )

            print(
                "Detected transcript language:",
                detected_language
            )

        except Exception as e:

            print(
                "⚠️ Language detection failed:",
                repr(e)
            )

            detected_language = None

        # -----------------------------------
        # Translate only if necessary
        # -----------------------------------

        if detected_language == "en":

            print(
                "🇬🇧 Transcript is already in English. "
                "Skipping translation."
            )

            english_transcription = transcription

        else:

            print(
                "🌍 Transcript is not English. "
                "Translating to English..."
            )

            english_transcription = (
                translate_transcript_to_english(
                    transcription
                )
            )

            if not english_transcription:

                return JsonResponse(
                    {
                        'error': (
                            'Failed to translate transcript to English'
                        )
                    },
                    status=500
                )

        # -----------------------------------
        # Generate tutorial
        # -----------------------------------

        tutorial = generate_tutorial_from_transcript(
            english_transcription
        )

        if not tutorial:

            return JsonResponse(
                {
                    'error': 'Failed to generate tutorial'
                },
                status=500
            )

        # -----------------------------------
        # Save tutorial
        # -----------------------------------

        new_tutorial = Tutorial.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            youtube_text=tutorial,
            transcript=english_transcription
        )

        new_tutorial.save()

        # -----------------------------------
        # Return tutorial
        # -----------------------------------

        return JsonResponse(
            {
                'content': tutorial
            }
        )

    except Exception as e:

        print(
            "SERVER ERROR:",
            e
        )

        return JsonResponse(
            {
                'error': f'Server error: {str(e)}'
            },
            status=500
        )









# # ---------------- TRANSCRIPT FUNCTIONS ---------------- #
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



def split_transcript_into_chunks(transcript, max_chars=12000):
    """

    Split a transcript into manageable chunks without cutting
    words unnecessarily.
    """

    words = transcript.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1

        if current_length + word_length > max_chars:
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            current_chunk = [word]
            current_length = word_length

        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks









def translate_transcript_to_english(transcription):
    """
    Translate a non-English transcript into English using Groq.

    The translation must preserve the original information,
    meaning, order, and important details.

    The model must not summarize, explain, expand, interpret,
    or add information that is not present in the transcript.
    """

    try:
        # -----------------------------------
        # Validate transcript
        # -----------------------------------

        if not transcription or not transcription.strip():
            print("❌ No transcript provided for translation")
            return None

        # -----------------------------------
        # Get Groq API key
        # -----------------------------------

        api_key = os.getenv("GROQ_API_KEY", "").strip()

        if not api_key:
            print("❌ Groq API key not found")
            return None

        # -----------------------------------
        # Groq client
        # -----------------------------------

        client = Groq(
            api_key=api_key,
            max_retries=0
        )

        # -----------------------------------
        # Translation prompt
        # -----------------------------------

        prompt = f"""
You are a professional translator for SmartNotes.

Translate the transcript below into clear, natural English.

Your task is ONLY to translate the transcript.

STRICT RULES:

1. Translate the entire transcript.
2. Preserve the original meaning exactly.
3. Do NOT summarize the transcript.
4. Do NOT explain anything.
5. Do NOT interpret what the speaker meant beyond the words provided.
6. Do NOT add facts, examples, explanations, opinions, conclusions, or context.
7. Do NOT remove information from the transcript.
8. Do NOT expand short statements into longer explanations.
9. Do NOT repeat information that appears only once in the original.
10. Preserve names, dates, places, numbers, terminology, examples,
    technical terms, and other important details.
11. Preserve the original order of information.
12. Preserve the structure of the speaker's ideas as closely as possible.
13. If the speaker repeats something, preserve the repetition where
    it is meaningful to the original transcript.
14. Do not turn spoken content into a summary or lecture note.
15. Do not add a conclusion.
16. Do not add headings unless they are clearly present in the original.
17. Do not add comments about the quality or meaning of the transcript.
18. Do not mention that you are translating.
19. Do not mention these instructions.
20. Return ONLY the translated transcript.

IMPORTANT:

The transcript may contain:
- informal speech
- incomplete sentences
- grammatical errors
- transcription mistakes
- repeated words
- filler words

Translate the intended meaning faithfully, but do not invent
information to "fix" or complete something that is unclear.

If a statement is unclear in the original transcript, translate
it as faithfully as possible without guessing additional information.

SOURCE TRANSCRIPT:

{transcription}

TRANSLATED ENGLISH TRANSCRIPT:
"""

        # -----------------------------------
        # Generate translation
        # -----------------------------------

        max_attempts = 2

        for attempt in range(1, max_attempts + 1):

            try:

                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.1,

                    max_tokens=16000,
                )

                translated = (
                    completion
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

                # -----------------------------------
                # Track actual token usage
                # -----------------------------------

                if completion.usage:

                    print(
                        "Translation usage:"
                    )

                    print(
                        "Input tokens:",
                        completion.usage.prompt_tokens
                    )

                    print(
                        "Output tokens:",
                        completion.usage.completion_tokens
                    )

                    print(
                        "Total tokens:",
                        completion.usage.total_tokens
                    )

                # -----------------------------------
                # Validate response
                # -----------------------------------

                if translated:

                    print(
                        "✅ Transcript translation "
                        "completed successfully"
                    )

                    return translated

                print(
                    f"⚠️ Translation attempt "
                    f"{attempt} returned empty content"
                )

            except Exception as e:

                print(
                    f"❌ Transcript translation attempt "
                    f"{attempt} failed:",
                    repr(e)
                )

                if attempt < max_attempts:
                    print("🔄 Retrying translation...")
                    time.sleep(2)

        print(
            "❌ Translation failed "
            "after all attempts"
        )

        return None

    except Exception as e:

        print(
            "❌ Translation fatal error:",
            repr(e)
        )

        traceback.print_exc()

        return None













def generate_tutorial_from_transcript(transcription):
    """
    Generate complete educational tutorial/lecture notes
    from a transcript using Groq GPT-OSS 20B.

    The entire transcript is sent in one request.
    No manual chunking is performed.
    """

    try:

        # -----------------------------------
        # Validate transcript
        # -----------------------------------

        if not transcription or not transcription.strip():

            print(
                "❌ No transcript provided "
                "for tutorial generation"
            )

            return None

        # -----------------------------------
        # Get Groq API key
        # -----------------------------------

        api_key = os.getenv(
            "GROQ_API_KEY",
            ""
        ).strip()

        if not api_key:

            print(
                "❌ Groq API key not found"
            )

            return None

        # -----------------------------------
        # Groq client
        # -----------------------------------

        client = Groq(
            api_key=api_key,
            max_retries=0
        )

        # -----------------------------------
        # Tutorial generation prompt
        # -----------------------------------

        prompt = f"""
You are an educational content generator for SmartNotes.

Based on the transcript below, create complete, clear,
detailed, and well-structured educational lecture notes.

The purpose of these notes is to allow a student to understand
and study the lecture without needing to listen to the original
recording again.

IMPORTANT REQUIREMENTS:

1. Cover the important information contained in the entire
   transcript.

2. Do not simply summarize the transcript.

3. Explain important concepts clearly and in enough depth
   for a student to learn from the notes.

4. Preserve important:
   - definitions
   - explanations
   - examples
   - processes
   - comparisons
   - names
   - dates
   - places
   - numbers
   - terminology
   - technical information

5. Do not invent information that is not supported by
   the transcript.

6. Do not introduce outside information.

7. Organize the notes into meaningful sections.

8. Use clear headings and subheadings where appropriate.

9. Use paragraphs, bullet points, and numbered lists when
   they make the material easier to understand.

10. When the transcript contains a comparison between concepts,
    present it in a simple readable format.

11. Do not use Markdown table syntax.

12. Do not use characters such as:
    | 
    ---
    to create tables.

13. Instead, use clearly labelled comparison sections.

For example:

Comparison: Type A vs Type B

Feature: Speed
Type A: Fast
Type B: Slow

Feature: Cost
Type A: High
Type B: Low

14. Keep technical terms, programming keywords, commands,
    and code examples accurate.

15. Use backticks for short technical syntax where appropriate.

16. Avoid unnecessary repetition.

17. Maintain a logical flow from the beginning of the lecture
    to the end.

18. Include all major topics discussed in the transcript.

19. End the notes with a concise conclusion that brings
    together the main concepts covered.

20. Where appropriate, include a short "Further Reading"
    section based ONLY on topics actually mentioned in
    the transcript. Do not invent books, websites, authors,
    or sources.

IMPORTANT:

The transcript may contain spoken-language repetition,
informal expressions, incomplete sentences, or transcription
errors.

Clean these up where necessary while preserving the intended
meaning.

Do not mention that the content came from a transcript.

Return only the completed educational lecture notes.

TRANSCRIPT:

{transcription}

LECTURE NOTES:
"""

        # -----------------------------------
        # Generate tutorial
        # -----------------------------------

        max_attempts = 2

        for attempt in range(
            1,
            max_attempts + 1
        ):

            try:

                completion = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.5,

                    max_tokens=16000,
                )

                tutorial = (
                    completion
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

                # -----------------------------------
                # Track actual token usage
                # -----------------------------------

                if completion.usage:

                    print(
                        "Tutorial generation usage:"
                    )

                    print(
                        "Input tokens:",
                        completion.usage.prompt_tokens
                    )

                    print(
                        "Output tokens:",
                        completion.usage.completion_tokens
                    )

                    print(
                        "Total tokens:",
                        completion.usage.total_tokens
                    )

                # -----------------------------------
                # Validate response
                # -----------------------------------

                if tutorial:

                    print(
                        "✅ Tutorial generated successfully"
                    )

                    return tutorial

                print(
                    f"⚠️ Tutorial generation attempt "
                    f"{attempt} returned empty content"
                )

            except Exception as e:

                print(
                    f"❌ Tutorial generation attempt "
                    f"{attempt} failed:",
                    repr(e)
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying tutorial generation..."
                    )

                    time.sleep(2)

        # -----------------------------------
        # All attempts failed
        # -----------------------------------

        print(
            "❌ Tutorial generation failed "
            "after all attempts"
        )

        return None

    except Exception as e:

        print(
            "❌ Tutorial generation fatal error:",
            repr(e)
        )

        traceback.print_exc()

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
     
    source = request.data.get("source", "web") 
    
    print("Payment Source:", source)

    
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
    "callback_url": (
    "https://smartnotes.cv/payment/callback"
    if source == "mobile"
    else "https://smartnotesfrontend.onrender.com/payment/callback"
    ),
    }

    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=data,
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

            
            # ----------------------------
            # Don't renew a subscription
            # that has been marked as
            # non-renewing/cancelled.
            # ----------------------------

            if subscription.cancel_at_period_end:

                

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
    # Subscription no longer renewing
    # ---------------------------------------

    if event_type == "subscription.not_renew":

        subscription_data = event.get("data", {})

        subscription_code = subscription_data.get(
            "subscription_code"
        )

        if not subscription_code:
            return Response(
                {
                    "message":
                        "Missing subscription code."
                },
                status=200
            )

        subscription = (
            Subscription.objects
            .filter(
                paystack_subscription_code=subscription_code
            )
            .first()
        )

        if subscription:

            subscription.cancel_at_period_end = True

            if not subscription.cancelled_at:
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
                    "Subscription marked as non-renewing."
            },
            status=200
        )

    # ---------------------------------------
    # Subscription disabled
    # ---------------------------------------

    if event_type == "subscription.disable":

        subscription_data = event.get("data", {})

        subscription_code = subscription_data.get(
            "subscription_code"
        )

        if not subscription_code:
            return Response(
                {
                    "message":
                        "Missing subscription code."
                },
                status=200
            )

        subscription = (
            Subscription.objects
            .filter(
                paystack_subscription_code=subscription_code
            )
            .first()
        )

        if subscription:

            subscription.cancel_at_period_end = True

            if not subscription.cancelled_at:
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
                    "Subscription marked as disabled."
            },
            status=200
        )

    # ---------------------------------------
    # Ignore other events
    # ---------------------------------------

    if event_type != "charge.success":

        return Response(
            {
                "message":
                    "Event ignored."
            },
            status=200
        )

    # ---------------------------------------
    # Successful payment
    # ---------------------------------------

    transaction = event.get("data", {})

    reference = transaction.get("reference")

    if not reference:

        return Response(
            {
                "detail":
                    "Missing transaction reference."
            },
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
            {
                "detail": str(e)
            },
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



def disable_paystack_subscription(subscription):

    if not subscription.paystack_subscription_code:
        return False, "No Paystack subscription found."

    if not subscription.paystack_email_token:
        return False, "Missing Paystack subscription verification token."

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

        return False, "Unable to contact Paystack."

    if not response_data.get("status"):

        return False, response_data.get(
            "message",
            "Unable to cancel the Paystack subscription."
        )

    return True, None


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

    success, error_message = disable_paystack_subscription(
        subscription
    )

    if not success:

        if error_message == "Unable to contact Paystack.":

            return Response(
                {
                    "detail": error_message
                },
                status=503
            )

        return Response(
            {
                "detail": error_message
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

        # print("🧠 Starting quiz generation...")

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
        with transaction.atomic():

            try:
                quiz = (
                    Quiz.objects
                    .select_for_update()
                    .get(
                        id=quiz_id,
                        user=request.user
                    )
                )
            except Quiz.DoesNotExist:
                return Response(
                    {"error": "Quiz not found."},
                    status=404
                )

            # Prevent submitting the same quiz twice
            if quiz.completed:
                return Response(
                    {"error": "This quiz has already been completed."},
                    status=400
                )

            answers = request.data.get("answers")

            if not answers:
                return Response(
                    {"error": "Please provide your answers."},
                    status=400
                )

            if not isinstance(answers, dict):
                return Response(
                    {"error": "Answers must be provided as an object."},
                    status=400
                )

            questions = quiz.questions.all().order_by("order")

            if not questions.exists():
                return Response(
                    {"error": "This quiz has no questions."},
                    status=400
                )

            question_list = list(questions)

            # IDs of questions that actually belong to this quiz
            expected_question_ids = {
                str(question.id)
                for question in question_list
            }

            # IDs submitted by the mobile app
            submitted_question_ids = {
                str(question_id)
                for question_id in answers.keys()
            }

            # Make sure every question has an answer
            missing_question_ids = (
                expected_question_ids - submitted_question_ids
            )

            if missing_question_ids:
                return Response(
                    {
                        "error": "Please answer all questions before submitting."
                    },
                    status=400
                )

            # Make sure the request does not contain unrelated questions
            unexpected_question_ids = (
                submitted_question_ids - expected_question_ids
            )

            if unexpected_question_ids:
                return Response(
                    {
                        "error": "Invalid question IDs were submitted."
                    },
                    status=400
                )

            score = 0
            results = []

            # Determine valid answer choices
            if quiz.question_type == "true_false":
                valid_answers = {"A", "B"}
            else:
                valid_answers = {"A", "B", "C", "D"}

            for question in question_list:

                question_id = str(question.id)

                selected_answer = answers.get(question_id)

                if selected_answer is None:
                    return Response(
                        {
                            "error": "Please answer all questions before submitting."
                        },
                        status=400
                    )

                selected_answer = str(
                    selected_answer
                ).strip().upper()

                # Validate the submitted answer choice
                if selected_answer not in valid_answers:
                    return Response(
                        {
                            "error": (
                                f"Invalid answer choice for question "
                                f"{question.id}."
                            )
                        },
                        status=400
                    )

                correct_answer = str(
                    question.correct_answer
                ).strip().upper()

                is_correct = (
                    selected_answer == correct_answer
                )

                if is_correct:
                    score += 1

                QuizAnswer.objects.create(
                    quiz=quiz,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct
                )

                results.append({
                    "question_id": question.id,
                    "order": question.order,
                    "selected_answer": selected_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                })

            total_questions = len(question_list)

            percentage = round(
                (score / total_questions) * 100
            )

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

    except Exception:
        traceback.print_exc()

        return Response(
            {
                "error": "An unexpected error occurred while submitting the quiz."
            },
            status=500
        )    
        
        
        
        
        
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def review_quiz_view(request, quiz_id):

    try:
        # -----------------------------------
        # Get quiz
        # -----------------------------------

        try:
            quiz = (
                Quiz.objects
                .prefetch_related("answers")
                .get(
                    id=quiz_id,
                    user=request.user
                )
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

            # -----------------------------------
            # Get selected answer
            # -----------------------------------

            selected_answer = ""

            if answer and answer.selected_answer:
                selected_answer = (
                    str(answer.selected_answer)
                    .strip()
                    .upper()
                )

            # -----------------------------------
            # Normalize correct answer
            # -----------------------------------

            correct_answer = (
                str(question.correct_answer)
                .strip()
                .upper()
            )

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
                correct_answer,
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

                    "correct_answer": correct_answer,
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

        print(
            "❌ QUIZ REVIEW ERROR:",
            repr(e)
        )
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
@permission_classes([IsAuthenticated])
def saved_quizzes_view(request):

    try:
        # -----------------------------------
        # Get user's quizzes
        # -----------------------------------

        quizzes = (
            Quiz.objects
            .filter(user=request.user)
            .select_related("lecture", "tutorial")
            .order_by("-created_at")
        )

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

        print(
            "❌ SAVED QUIZZES ERROR:",
            repr(e)
        )
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