import configparser
import json
import ast
import paramiko
import requests

# import requests
from celery import shared_task

from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission
from .models import ContainerTestModel, ScaleTestModel


# @shared_task(time_limit=200)
def setup_scale_eval(*args, **kwargs):
    eval_id = (
        kwargs["form_data"]["eval_id"] if "eval_id" in kwargs["form_data"] else None
    )
    if eval_id is None:
        raise RuntimeError
    scale_test = ScaleTestModel()
    scale_test.scale_min = kwargs["form_data"]["scale_min"]
    scale_test.scale_max = kwargs["form_data"]["scale_max"]
    scale_test.metric = kwargs["form_data"]["metric"]
    scale_test.window = kwargs["form_data"]["window"]
    scale_test.up_threshold = kwargs["form_data"]["up_threshold"]
    scale_test.down_threshold = kwargs["form_data"]["down_threshold"]
    scale_test.evaluation = Evaluation.objects.get(
        id=int(kwargs["form_data"]["eval_id"])
    )
    scale_test.save()


@shared_task(time_limit=200)
def do_scale_eval(*args, **kwargs):
    print("hello world")


# def give_marks(testpassed, testname):
#     marks = 0
#     message = ""
#     if testpassed:
#         marks = 1
#         message += testname + " test passed\n\n"
#     else:
#         message += testname + " test failed\n\n"
#     return marks, message
