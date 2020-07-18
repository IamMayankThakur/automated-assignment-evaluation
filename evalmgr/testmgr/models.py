from django.db import models
from facultymgr.models import Evaluation
from studentmgr.models import OverwriteStorage


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


class CodeEvalModel(models.Model):
    docker_file = models.FileField(
        blank=False, upload_to="conf/dockerfile/", storage=OverwriteStorage(), null=True
    )
    main_file = models.FileField(blank=False, upload_to="conf/mainfile/", null=True)
    expected_output_file = models.FileField(
        blank=False, upload_to="conf/expected_output/", null=True
    )
    command = models.TextField(blank=False, null=True)
    evaluation = models.ForeignKey(
        Evaluation, on_delete=models.CASCADE, null=True, blank=True
    )

    objects = models.Manager()

    class Meta:
        app_label = "facultymgr"
        managed = True


class CodeEvalTestModel(models.Model):
    test_name = models.TextField(default="hidden")
    sanity = models.BooleanField(default=False)
    length_input1 = models.TextField(blank=False)
    length_input2 = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        app_label = "facultymgr"
        managed = True


class ContainerTestModel(models.Model):
    container_name = models.TextField(blank=False)
    container_image = models.TextField(blank=False)
    ports_exposed = models.TextField(blank=True)
    connected_to_networks = models.TextField(blank=True)
    env_variables = models.TextField(blank=True)
    volumes = models.TextField(blank=True)
    commands = models.TextField(blank=True)
    num_cpus = models.IntegerField(blank=True,null=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        app_label = "facultymgr"
        managed = True


class ScaleTestModel(models.Model):
    service_name = models.TextField(blank=False)
    scale_min = models.IntegerField(blank=False)
    scale_max = models.IntegerField(blank=False)
    metric = models.TextField(blank=False)
    window = models.TextField(blank=False)
    up_threshold = models.TextField(blank=False)
    down_threshold = models.TextField(blank=False)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        app_label = "facultymgr"
        managed = True
