from django.db import models
from django.contrib.auth.models import AbstractUser
class CustomUser(AbstractUser):
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    address = models.TextField(max_length=150, null=True, blank=True)
    def __str__(self):
        return self.username










