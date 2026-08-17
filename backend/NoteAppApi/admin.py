from django.contrib import admin
from .models import Note, Contact, Task, Lecture, Tutorial, Subscription, Quiz, QuizAnswer, QuizQuestion

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

