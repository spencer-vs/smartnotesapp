from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

# Create your models here.

class Note(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
 
    
    def __str__(self):
       return self.title or 'untitled'
   
   
   
class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contact"
    )
   
    author = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
 
    
    def __str__(self):
       return self.author or 'unauthored'
   
   
   
   
class Task(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ToDo'
    )
    todo_title = models.CharField(max_length=100, blank=True)
    todo_list = models.TextField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    
    def __str__(self):
        return self.title or 'unititled'