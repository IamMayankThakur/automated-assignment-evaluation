from django.db import models
from django.utils import timezone
# Create your models here.


class Evaluation(models.Model):
    name = models.CharField(max_length=128, unique=True, blank=False)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    begins_on = models.DateTimeField(default=timezone.now)
    ends_on = models.DateTimeField(blank=False)