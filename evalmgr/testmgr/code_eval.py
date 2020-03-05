import configparser
import json
import ast

import requests
from celery import shared_task

from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission
from .models import CodeEvalTestModel


@shared_task(time_limit=200)
def setup_code_eval(*args, **kwargs):
    eval_id = kwargs["eval_id"] if "eval_id" in kwargs else None
    if eval_id is None:
        raise RuntimeError
    evaluation = Evaluation.objects.get(pk=eval_id)
    file = evaluation.conf_file.path
    c = configparser.ConfigParser()
    c.read(file)
    sections = c.sections()
    sections.remove("Settings")
    for s in sections:
        code_test = CodeEvalTestModel()
        code_test.test_name = s
        code_test.sanity = True if c[s]["sanity"] == "True" else False
        code_test.input1 = c[s]["input1"]
        code_test.input2 = c[s]["input2"]
        code_test.expected_output = c[s]["expected_output"]
        code_test.evaluation = Evaluation.objects.get(id=eval_id)
        code_test.save()


@shared_task(time_limit=200)
def do_code_eval(*args, **kwargs):
    return "okay"
