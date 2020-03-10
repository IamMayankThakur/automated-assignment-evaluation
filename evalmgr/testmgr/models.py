from django.db import models
from facultymgr.models import Evaluation


class ApiTestModel(models.Model):
    test_name = models.TextField(default="hidden")
    sanity = models.BooleanField(default=False)
    api_endpoint = models.TextField(blank=False)
    api_method = models.CharField(max_length=16, blank=False, null=True)
    api_message_body = models.TextField(blank=True)
    expected_status_code = models.IntegerField(blank=False)
    expected_response_body = models.TextField(blank=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        app_label = "facultymgr"
        managed = True


class ContainerTestModel(models.Model):
    test_name = models.TextField(default="hidden")
    container_name = models.TextField(blank=False)
    container_image = models.TextField(blank=False)
    ports_exposed = models.TextField(blank=True)
    networks = models.TextField(blank=True)
    connected_to_networks = models.TextField(blank=True)
    env_variables = models.TextField(blank=True)
    volumes = models.TextField(blank=True)
    commands = models.TextField(blank=True)
    num_cpus = models.IntegerField(blank=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    objects = models.Manager()

    class Meta:
        app_label = "facultymgr"
        managed = True
