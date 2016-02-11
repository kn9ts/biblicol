from django.db import models
from django.utils import timezone


class Subscribers(models.Model):
    email_address = models.CharField(max_length=256, unique=True)
    activation_code = models.CharField(max_length=256, unique=True)
    is_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    modified_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
