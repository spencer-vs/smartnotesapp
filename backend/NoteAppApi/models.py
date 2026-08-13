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

    PLAN_CHOICES = [
        ("free", "Free Trial"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="trial",
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="free",
    )

    trial_start = models.DateTimeField(
        default=timezone.now
    )

    trial_end = models.DateTimeField(
        default=default_trial_end
    )

    subscription_start = models.DateTimeField(
        null=True,
        blank=True,
    )

    subscription_end = models.DateTimeField(
        null=True,
        blank=True,
    )
    
    cancelled_at = models.DateTimeField(null=True, blank=True)

    cancel_at_period_end = models.BooleanField(default=False)

    paystack_customer_code = models.CharField(
        max_length=255,
        blank=True,
    )

    paystack_subscription_code = models.CharField(
        max_length=255,
        blank=True,
    )
    
    paystack_reference = models.CharField(
    max_length=255,
    blank=True,
    unique=True,
    null=True
    )

    paystack_transaction_id = models.CharField(
    max_length=255,
    blank=True,
    null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def days_left(self):
        now = timezone.now()

        if self.status == "trial":
            return max((self.trial_end - now).days, 0)

        if self.status == "active" and self.subscription_end:
            return max((self.subscription_end - now).days, 0)

        return 0

    @property
    def premium(self):
        now = timezone.now()

        if self.status == "trial":
            return self.trial_end > now

        if self.status == "active":
            return (
                self.subscription_end is not None
                and self.subscription_end > now
            )

        return False

    @property
    def is_trial(self):
        return self.status == "trial"

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def is_expired(self):
        return self.status == "expired"

    @property
    def is_cancelled(self):
        return self.status == "cancelled"
    
    @property
    def renewal_date(self):

       if self.status in ["trial", "expired"]:
        return self.trial_end

       if self.status == "active":
        return self.subscription_end

       if self.status == "cancelled":
        return self.subscription_end

       return None

    def activate_monthly(self):
        now = timezone.now()

        self.plan = "monthly"
        self.status = "active"
        self.subscription_start = now
        self.subscription_end = now + timedelta(days=30)
        self.save()

    def activate_yearly(self):
        now = timezone.now()

        self.plan = "yearly"
        self.status = "active"
        self.subscription_start = now
        self.subscription_end = now + timedelta(days=365)
        self.save()

    def expire(self):
        self.status = "expired"
        self.save(update_fields=["status"])

    def cancel(self):
        self.status = "cancelled"
        self.save(update_fields=["status"])

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()} ({self.status})"