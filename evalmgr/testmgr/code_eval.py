import configparser
import json
import ast

import requests
from celery import shared_task

from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission
from .models import CodeEvalTestModel, CodeEvalModel
from random import randint
import docker
import os

# path = (
#     "/home/nihali/work/8thsem/code/automated-assignment-evaluation/evalmgr/media/"
# )


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
        code_test.length_input1 = c[s]["length_input1"]
        code_test.length_input2 = c[s]["length_input2"]
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
    submission = Submission.objects.get(id=sub_id)
    code_file = submission.source_code_file
    code_eval = CodeEvalModel.objects.get(evaluation=eval_id)
    main_file = code_eval.main_file
    command = code_eval.command
    expected_output_file = code_eval.expected_output_file
    print("main_file:", main_file)
    print("code_file:", code_file)

    normal_tests = CodeEvalTestModel.objects.filter(evaluation=eval_id)
    print("normal_tests:", normal_tests)
    marks, message = run_tests(
        normal_tests, code_file, main_file, command, expected_output_file
    )
    submission.marks = marks
    submission.message = message
    submission.save()
    return


def random_with_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def run_tests(test_objects, code_file, main_file, command, expected_output_file):

    path = os.getcwd() + "/media/"
    print(path)
    f = open(path + "conf/expected_output/input.txt", "w")
    for test in test_objects:
        length_input1 = test.length_input1
        length_input2 = test.length_input2
        len_input1 = int(length_input1)
        len_input2 = int(length_input2)
        print("len_input1:", len_input1)
        print("len_input2:", len_input2)

        input1 = random_with_digits(len_input1)
        input2 = random_with_digits(len_input2)
        print("input1", input1)
        print("input2", input2)
        f.write(str(input1) + "\n")
        f.write(str(input2) + "\n")

    f.close()
    client = docker.from_env()
    # print("IMAGES", client.images.list())
    # client.images.build(path= path1 + 'media/conf/dockerfile',tag={"image2"})

    exp_output = str(expected_output_file)
    code_file2 = str(code_file)
    folder_exp_output = "mnt/vol1/conf/expected_output/"
    folder_student_sub = "mnt/vol1/source/api_test/"

    arg_0 = exp_output.rsplit("/", 1)[1]
    arg_1 = code_file2.rsplit("/", 1)[1]
    arg_2 = folder_exp_output
    arg_3 = folder_student_sub

    res = 1
    try:

        client.containers.run(
            image="gcc",
            stdout=True,
            detach=False,
            volumes={path: {"bind": "/mnt/vol1", "mode": "rw",}},
            # command = "sh -c 'gcc mnt/vol1/conf/expected_output/{0} && ./a.out < mnt/vol1/conf/expected_output/input.txt > mnt/vol1/conf/expected_output/output_expected.txt && gcc -o foo mnt/vol1/source/api_test/{1} && ./foo < mnt/vol1/conf/expected_output/input.txt > output.txt && diff output.txt mnt/vol1/conf/expected_output/output_expected.txt'".format(arg_0,arg_1)
            # command = "sh -c 'gcc {2}{0} && ./a.out < {2}input.txt > {2}output_expected.txt && gcc -o foo {3}{1} && ./foo < {2}input.txt > output.txt && diff output.txt {2}output_expected.txt'".format(arg_0,arg_1,arg_2,arg_3)
            command=command.format(arg_0, arg_1, arg_2, arg_3),
        )
    except Exception:
        res = -1

    # res = result.decode("utf-8")
    # awk ' NR==FNR { a[$0]; next } !($0 in a){ print $1; exit } ' file2 file1
    if res == 1:
        print("yes")
        marks = 10
        message = "done!"
    else:
        print("No")
        marks = 0
        message = "Test case failed"
    for con in client.containers.list(all=True):
        con.remove()

    return marks, message
