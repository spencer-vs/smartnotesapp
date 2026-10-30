from django.contrib import admin
from .models import Note, Contact, Task, TaskItem, Lecture, Tutorial, Subscription, Quiz, QuizAnswer, QuizQuestion, Package, PackagePurchase, UserCreditBalance, CreditTransaction

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
#     list_display = ("id", "todo_title", "todo_list", "timetable_type")
#     search_fields = ('ToDo',)
  
  
class TaskItemInline(admin.TabularInline):
    model = TaskItem
    extra = 0

    fields = (
        'description',
        'date',
        'timetable_type',
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
        'timetable_type',
        'week_start',
        'week_end',
        'completed',
        "reminder_enabled",
        'created_at',
        'is_deleted',
    )

    list_filter = (
        'is_deleted',
        'timetable_type',
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
    list_display = ("id", "title", "lecture", "transcript", "created_at")
    search_fields = ("Lectures",)
    
    

    
    
@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ("id", "youtube_title", "youtube_text", "youtube_link", "transcript")
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





@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "level",
        "category",
        "price_ngn",
        "price_usd",
        "audio_credits",
        "youtube_credits",
        "quiz_credits",
        "is_active",
    )

    list_filter = (
        "level",
        "category",
        "is_active",
    )

    search_fields = (
        "code",
        "google_play_product_id",
    )

    list_editable = (
        "is_active",
    )

    ordering = ("display_order",)


@admin.register(PackagePurchase)
class PackagePurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "package",
        "amount_paid",
        "currency",
        "provider",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "provider",
        "currency",
    )

    search_fields = (
        "user__username",
        "user__email",
        "order_id",
    )

    readonly_fields = (
        "purchase_token",
        "order_id",
        "purchased_at",
        "verified_at",
        "created_at",
        "updated_at",
    )


@admin.register(UserCreditBalance)
class UserCreditBalanceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "audio_credits",
        "youtube_credits",
        "quiz_credits",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "transaction_type",
        "feature",
        "amount",
        "balance_after",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "feature",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "description",
        "idempotency_key",
    )

    readonly_fields = (
        "user",
        "purchase",
        "transaction_type",
        "feature",
        "amount",
        "balance_after",
        "description",
        "idempotency_key",
        "created_at",
    )