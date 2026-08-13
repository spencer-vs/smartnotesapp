from rest_framework import serializers
from django.contrib.auth import get_user_model
from . models import Note, Contact, Task, Lecture, Tutorial, Subscription
from django.utils import timezone


User = get_user_model

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'modified_at']
        read_only_fields = [ 'created_at', 'modified_at']
        

        
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "author", "email", "phone", "message", "created_at"]
        read_only_fields = ["created_at"]
        
        
class TaskSerializer(serializers.ModelSerializer):
    
   class Meta:   
    model = Task
    fields = ["id", "todo_title", "todo_list", "created_at"]
    read_only_fields = ["created_at"]
    
    
    
class LectureSerializer(serializers.ModelSerializer):
   class Meta:
        model = Lecture
        fields = ["id", "lecture", "created_at"]
        # read_only_fields = ["created_at"]
    
    
class TutorialSerializer(serializers.ModelSerializer):
    
  class Meta:  
    model = Tutorial
    fields = ["id", "youtube_title", "youtube_text", "youtube_link", "created_at"]
    # read_only_fields = ["created_at"]
    
    
from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):

    plan_name = serializers.CharField(
        source="get_plan_display",
        read_only=True
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True
    )
    
    
    
    

    class Meta:
        model = Subscription

        fields = [
            "plan",
            "plan_name",

            "status",
            "status_name",

            "premium",
            "days_left",

            "trial_start",
            "trial_end",

            "subscription_start",
            "subscription_end",
            
            "renewal_date",
            
            "cancelled_at",
            "cancel_at_period_end",

            "is_trial",
            "is_active",
            "is_expired",
            "is_cancelled",
        ]
        
   