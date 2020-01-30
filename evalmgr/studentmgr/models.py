from django.db import models
from ..facultymgr.models import Evaluation
# Create your models here.


class Team(models.Model):
    team_name = models.CharField(max_length=64, blank=False, unique=True)
    email_member_1 = models.EmailField(unique=True, blank=False)
    email_member_2 = models.EmailField(unique=True, blank=True)
    email_member_3 = models.EmailField(unique=True, blank=True)
    email_member_4 = models.EmailField(unique=True, blank=True)

    def __str__(self):
        return str(self.team_name)


class Submission(models.Model):
    team = models.ForeignKey(Team)
    evaluation = models.ForeignKey(Evaluation)
    marks = models.FloatField()

    def __str__(self):
        return str(self.id)


class ApiTestSubmission(Submission):
    public_ip_address = models.URLField(blank=False)
    source_code_file = models.FileField(upload_to='source/api_test/')
    above_specification = models.TextField()
    above_specification_file = models.FileField(upload_to='source/above_api_specification/')
