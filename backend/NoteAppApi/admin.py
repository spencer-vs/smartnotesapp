from django.contrib import admin
from .models import Note, Contact, Task, TaskItem, Lecture, Tutorial, Subscription, Quiz, QuizAnswer, QuizQuestion

# Register your models here.
@admin.register(Note)
class NotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'modified_at')
    search_fields = ('title',)


@admin.register(Contact)   
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', "author", "email", "phone", "message",)
    search_fields = ('author',)
    
    
# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = ("id", "todo_title", "todo_list")
#     search_fields = ('ToDo',)
  
  
class TaskItemInline(admin.TabularInline):
    model = TaskItem
    extra = 0

    fields = (
        'description',
        'date',
        'start_time',
        'end_time',
        'completed',
        'order',
    )

    ordering = (
        'date',
        'start_time',
        'order',
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'todo_title',
        'user',
        'week_start',
        'week_end',
        'completed',
        'created_at',
        'is_deleted',
    )

    list_filter = (
        'is_deleted',
        'week_start',
        'week_end',
        'completed',
    )

    search_fields = (
        'todo_title',
        'user__username',
        'user__email',
    )

    readonly_fields = (
        'created_at',
    )

    inlines = [
        TaskItemInline,
    ]  
  

@admin.register(TaskItem)
class TaskItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'task',
        'description',
        'date',
        'start_time',
        'end_time',
        'completed',
        'order',
    )

    list_filter = (
        'completed',
        'date',
    )

    search_fields = (
        'description',
        'task__todo_title',
        'task__user__username',
    )

    ordering = (
        'date',
        'start_time',
        'order',
    )



  
@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "lecture", "created_at")
    search_fields = ("Lectures",)
    
    

    
    
@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ("id", "youtube_title", "youtube_text", "youtube_link")
    search_fields = ("Tutorials", )
    
    

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status",
        "trial_end",
        "subscription_end",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    ordering = (
        "-created_at",
    )
    
    



@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "get_source",
        "difficulty",
        "question_type",
        "number_of_questions",
        "score",
        "completed",
        "created_at",
    )

    list_filter = (
        "difficulty",
        "question_type",
        "completed",
        "created_at",
    )

    search_fields = (
        "user__username",
        "lecture__lecture",
        "tutorial__youtube_title",
        "tutorial__youtube_text",
    )

    readonly_fields = (
        "created_at",
        "completed_at",
    )

    def get_source(self, obj):
        if obj.lecture:
            return f"Lecture: {obj.lecture}"
        elif obj.tutorial:
            return f"YouTube: {obj.tutorial.youtube_title}"
        return "No source"

    get_source.short_description = "Source"


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quiz",
        "order",
        "question",
        "correct_answer",
    )

    list_filter = (
        "quiz__difficulty",
        "quiz__question_type",
    )

    search_fields = (
        "question",
        "quiz__user__username",
    )

    ordering = (
        "quiz",
        "order",
    )


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quiz",
        "question",
        "selected_answer",
        "is_correct",
        "answered_at",
    )

    list_filter = (
        "is_correct",
        "answered_at",
    )

    search_fields = (
        "quiz__user__username",
        "question__question",
    )





# Finalize Task and TaskItem models
# Update Django admin so weekly tasks and checklist items are easy to inspect
# Create serializers
# Rewrite Groq scheduling to return structured Monday–Saturday data
# Rewrite create_task()
# title + checklist items from user
# enforce one active task
# calculate next Monday → Saturday
# send items to Groq
# validate Groq's response
# create TaskItem records
# Rewrite task_detail()
# Rewrite get_all_task() to return weekly Task records with progress
# Add the simple checklist completion operation
# Change deletion to soft delete
# Update URLs
# Test the complete backend in Postman
# Then move to the Create Task → Task Display → Tasks/weekly history mobile flow.