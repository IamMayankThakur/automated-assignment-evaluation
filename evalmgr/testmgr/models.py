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


class CodeEvalModel(models.Model):
    dock_file = models.FileField(blank=False, upload_to="conf/eval/")
    main_file = models.FileField(blank=False, upload_to="conf/eval/")
    evaluation = models.ForeignKey(
        Evaluation, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        app_label = "facultymgr"
        managed = True


class CodeEvalTestModel(models.Model):
    test_name = models.TextField(default="hidden")
    sanity = models.BooleanField(default=False)
    input1 = models.TextField(blank=False)
    input2 = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        app_label = "facultymgr"
        managed = True
