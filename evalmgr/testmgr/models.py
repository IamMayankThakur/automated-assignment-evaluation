from django.db import models
from facultymgr.models import Evaluation


class ApiTestModel(models.Model):
    sanity = models.BooleanField(default=False)
    api_endpoint = models.TextField(blank=False)
    api_method = models.CharField(max_length=16, blank=False, null=True)
    api_message_body = models.TextField(blank=True)
    expected_status_code = models.IntegerField(blank=False)
    expected_response_body = models.TextField(blank=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        app_label = 'facultymgr'
        managed = True
