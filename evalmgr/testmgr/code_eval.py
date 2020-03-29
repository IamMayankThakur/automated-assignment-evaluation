import configparser
import json
import ast

import requests
from celery import shared_task

from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission, SubmissionCodeEval
from .models import CodeEvalTestModel, CodeEvalModel
from random import randint
import docker
import os


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
        code_test.input1 = c[s]["length_input1"]
        code_test.input2 = c[s]["length_input2"]
        code_test.expected_output = c[s]["expected_output"]
        code_test.evaluation = Evaluation.objects.get(id=eval_id)
        code_test.save()


@shared_task(time_limit=200)
def do_code_eval(*args, **kwargs):

    marks = 0
    message = ""
    sub_id = kwargs.get("sub_id", None)
    eval_id = kwargs.get("eval_id", None)
    if sub_id is None:
        print("No sub id")
        raise RuntimeError
    print("evaluation started")
    submission = SubmissionCodeEval.objects.get(id=sub_id)
    code_file = submission.source_code_file
    code_eval = CodeEvalModel.objects.get(evaluation=eval_id)
    main_file = code_eval.main_file
    print("main_file:", main_file)
    print("code_file:", code_file)

    normal_tests = CodeEvalTestModel.objects.filter(sanity=True)
    print("normal_tests:", normal_tests)
    marks, message = run_tests(normal_tests, code_file, main_file)
    submission.marks = marks
    submission.message = message
    submission.save()
    return "okay"


def run_tests(test_objects, code_file, main_file):
    path = (
        "/home/nihali/work/8thsem/code/automated-assignment-evaluation/evalmgr/media/"
    )
    f = open(path + "conf/add_func/input.txt", "w")
    for test in test_objects:
        length_input1 = test.length_input1
        length_input2 = test.length_input2
        input1 = length_input1
        input2 = length_input2
        f.write(input1 + "\n")
        f.write(input2 + "\n")

    f.close()
    client = docker.from_env()
    # print("IMAGES", client.images.list())
    # client.images.build(path= path1 + 'media/conf/dockerfile',tag={"image2"})
    code_file2 = str(code_file)
    file_name = code_file2.rsplit("/", 1)[1]
    result = client.containers.run(
        image="image3",
        stdout=True,
        detach=False,
        volumes={
            "/home/nihali/work/8thsem/code/automated-assignment-evaluation/evalmgr/media/": {
                "bind": "/mnt/vol1",
                "mode": "rw",
            }
        },
        command="sh -c 'gcc mnt/vol1/conf/add_func/add.c && ./a.out < mnt/vol1/conf/add_func/input.txt > mnt/vol1/conf/add_func/output_expected.txt && gcc -o foo mnt/vol1/source/code_eval/{0} && ./foo < mnt/vol1/conf/add_func/input.txt > output.txt && diff output.txt mnt/vol1/conf/add_func/output_expected.txt'".format(
            file_name
        ),
    )
    print(result.decode("utf-8"))
    res = result.decode("utf-8")
    if res == "":
        print("yes")
        marks = 10
        message = "done!"
    else:
        print("No")
        marks = 0
        message = "Test case failed:" + "Here are the inputs:"
    for con in client.containers.list(all=True):
        con.remove()

    return marks, message
