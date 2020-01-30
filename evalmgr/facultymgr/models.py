from django.db import models
from django.utils import timezone
# Create your models here.


class FacultyProfile(models.Model):
    name = models.TextField(blank=False)
    email = models.EmailField(blank=False, unique=True)


class Evaluation(models.Model):
    conf_file = models.FileField(blank=False, upload_to='conf/eval/')
    name = models.CharField(max_length=128, unique=True, blank=False)
    type = models.IntegerField(blank=False)
    access_code = models.IntegerField(blank=False, unique=True)
    created_by = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    begins_on = models.DateTimeField(default=timezone.now)
    ends_on = models.DateTimeField(blank=True)
