from django.contrib import admin
from .models import Note, Contact, Task, Lecture, Tutorial

# Register your models here.
@admin.register(Note)
class NotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'modified_at')
    search_fields = ('title',)


@admin.register(Contact)   
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', "author", "email", "phone", "message",)
    search_fields = ('author',)
    
    
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "todo_title", "todo_list")
    search_fields = ('ToDo',)
    
@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("id", "lecture", "created_at")
    search_fields = ("Lectures",)
    
    
@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ("id", "youtube_title", "youtube_text", "youtube_link")
    search_fields = ("youtube_text", )
    
    