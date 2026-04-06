from rest_framework import serializers
from django.contrib.auth import get_user_model
from . models import Note, Contact, Task, Lecture, Tutorial


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
    model = Task
    fields = ["id", "todo_title", "todo_list", "created_at"]
    read_only_fields = ["created_at"]
    
    
    
class LectureSerializer(serializers.ModelSerializer):
    model = Lecture
    fields = ["id", "lecture", "created_at"]
    read_only_fields = ["created_at"]
    
    
class TutorialSerializer(serializers.ModelSerializer):
    model = Tutorial
    fields = ["id", "youtube_title", "youtube_text", "youtube_link"]
    read_only_fields = ["created_at"]