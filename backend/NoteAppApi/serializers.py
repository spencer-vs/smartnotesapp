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
    
    
class SubscriptionSerializer(serializers.ModelSerializer):
    days_left = serializers.SerializerMethodField()
    premium = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            "status",
            "trial_end",
            "subscription_end",
            "days_left",
            "premium"
        ]
        
    def get_days_left(self, obj):
        now = timezone.now()
        
        if obj.status == "trial":
            delta = obj.trial_end - now
        elif obj.status == "active" and obj.subscription_end:
            delta = obj.subscription_end - now
        else:
            return 0
        return max(delta.days, 0)
    
    
    def get_premium(self, obj):
        now = timezone.now()
        
        if obj.status == "active":
            return obj.subscription_end and obj.subscription_end > now
        if obj.status == "trial":
            return obj.trial_end > now
        return False
            
        