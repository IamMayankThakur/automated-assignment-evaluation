import os

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone

from facultymgr.models import Evaluation


# Create your models here.


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name


class Team(models.Model):
    team_name = models.CharField(max_length=64, blank=False, unique=True)
    email_member_1 = models.EmailField(unique=True, blank=False)
    email_member_2 = models.EmailField(blank=True)
    email_member_3 = models.EmailField(blank=True)
    email_member_4 = models.EmailField(blank=True)

    def __str__(self):
        return str(self.team_name)


class Submission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    username = models.CharField(max_length=128, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    marks = models.FloatField(default=-1)
    message = models.TextField(default="Probably not evaluated yet")
    faculty_message = models.TextField(blank=True)
    public_ip_address = models.URLField(blank=False)
    source_code_file = models.FileField(upload_to="source/api_test/")
    above_specification_choice = models.CharField(max_length=256, blank=True, null=True)
    above_specification = models.TextField()
    above_specification_file = models.FileField(
        upload_to="source/above_api_specification/"
    )
    private_key_file = models.FileField(
        upload_to="key", storage=OverwriteStorage(), blank=True
    )

    def __str__(self):
        return str(self.id)


class SubmissionAssignment3(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    users_source_file = models.FileField(
        upload_to="source/users", storage=OverwriteStorage(), blank=True
    )
    rides_source_file = models.FileField(
        upload_to="source/rides", storage=OverwriteStorage(), blank=True
    )
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    lb_ip = models.CharField(max_length=128, blank=True)
    users_ip = models.CharField(max_length=128, blank=True)
    rides_ip = models.CharField(max_length=128, blank=True)
    marks = models.FloatField(default=-1)
    message = models.TextField()

    def __str__(self):
        return str(self.id)
