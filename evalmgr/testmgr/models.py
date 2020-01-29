from django.db import models


class ApiTestModel(models.Model):
    api_endpoint = models.TextField(blank=False)
    api_method = models.IntegerField(blank=False)
    api_message_body = models.TextField(blank=True)
    expected_status_code = models.IntegerField(blank=False)
    expected_response_body = models.TextField(blank=True)
    evaluation = models.IntegerField(blank=False)