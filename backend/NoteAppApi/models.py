from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

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
        return self.todo_title or 'Task'
    
    
    
    




class Lecture(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='Lecture'
    )
    lecture = models.TextField(null=True, blank=True) 
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    status=models.CharField(max_length=20, default="processing")
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    
    def __str__(self):
        return self.lecture or 'Lectures'
    
    


class Tutorial(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='Tutorial'
    )
    youtube_title = models.CharField(max_length=100, null=True, blank=True)
    youtube_text = models.TextField(null=True, blank=True)
    youtube_link = models.CharField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.youtube_title or "Tutorials"
    
    
    
    
    
def default_trial_end():
    return timezone.now() + timedelta(days=14)

class Subscription(models.Model):
    STATUS_CHOICES = [
        ("trial", "Trial"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="trial"
        )
    
    trial_start = models.DateTimeField(default=timezone.now)
    
    trial_end = models.DateTimeField(default=default_trial_end)
    
    subscription_start =  models.DateTimeField(null=True, blank=True)
    
    subscription_end = models.DateTimeField(null=True, blank=True)
    
    paystack_customer_code = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user} ({self.status})"