from django.db import models
from facultymgr.models import Evaluation
from django.utils import timezone
# Create your models here.


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
    timestamp = models.DateTimeField(default=timezone.now)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    marks = models.FloatField(default=-1)
    message = models.TextField()
    public_ip_address = models.URLField(blank=False)
    source_code_file = models.FileField(upload_to='source/api_test/')
    above_specification_choice = models.CharField(max_length=256, blank=True, null=True)
    above_specification = models.TextField()
    above_specification_file = models.FileField(upload_to='source/above_api_specification/')

    def __str__(self):
        return str(self.id)

