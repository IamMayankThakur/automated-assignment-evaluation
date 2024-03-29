from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class Evaluation(models.Model):
    conf_file = models.FileField(blank=False, upload_to="conf/eval/")
    name = models.CharField(max_length=128, unique=False, blank=False)
    type = models.IntegerField(blank=False, null=True)
    access_code = models.CharField(max_length=256, blank=False, unique=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    begins_on = models.DateTimeField(default=timezone.now)
    ends_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.name)
