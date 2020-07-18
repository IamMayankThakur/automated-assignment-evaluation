import configparser
import json
import ast
import paramiko
import requests
import os
import socket
import subprocess
import time

# import requests
from celery import shared_task

from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission
from .models import ScaleTestModel
from paramiko.ssh_exception import (
    BadHostKeyException,
    AuthenticationException,
    SSHException,
)

# @shared_task(time_limit=200)
def setup_scale_eval(*args, **kwargs):
    eval_id = (
        kwargs["form_data"]["eval_id"] if "eval_id" in kwargs["form_data"] else None
    )
    if eval_id is None:
        raise RuntimeError
    scale_test = ScaleTestModel()
    scale_test.service_name = kwargs["form_data"]["service_name"]
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


# Scale max 3
# scale min 1
# window 30s
# up threshold 10
# down threshold 5
# Requests per second to send per instance = int(up threshold + down threshold / 2)
# wrk -t1 -c1 -d -R


@shared_task(time_limit=200)
def do_scale_eval(*args, **kwargs):
    sub = Submission.objects.get(id=kwargs.get("sub_id"))
    service_address = sub.public_ip_address
    username = sub.username
    path_to_key = sub.private_key_file.path
    tests = ScaleTestModel.objects.filter(evaluation=sub.evaluation)
    marks = 0
    message = ""
    faculty_message = ""
    ip = service_address.split(":", 1)[0]
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, username=username, key_filename=path_to_key)
    except (
        AuthenticationException,
        SSHException,
        BadHostKeyException,
        UnicodeDecodeError,
        socket.gaierror,
    ):
        # except Exception as e:
        message += "Fatal Error.! Check if your instance is running / port is open / pem file is correct etc"
        faculty_message += "Fatal Error.! Check if your instance is running / port is open / pem file is correct etc"
        sub.message = message
        sub.faculty_message = faculty_message
        sub.marks = marks
        sub.save()
        return

    for test in tests:
        stdin, stdout, stderr = ssh.exec_command(
            "sudo docker service ps " + test.service_name
        )
        error_output = stderr.read().decode()

        if len(error_output) != 0:
            message += (
                "Fatal Error.! Service '" + test.service_name + "' is not running\n"
            )
            sub.message = message
            sub.marks = marks
            sub.save()
            continue

        stdin, stdout, stderr = ssh.exec_command(
            "sudo docker service ls -f name="
            + test.service_name
            + " --format {{.Replicas}}"
        )
        output = stdout.read().decode()
        if len(output) == 0 or test.scale_min != int(output.split("/")[0]):
            message += "Minimum scale test case failed\n"
        else:
            message += "Servic scaled to "+str(test.scale_min)+" instances in the given time\n"
            marks += 1

        Requests = (
            int((int(test.up_threshold) + int(test.down_threshold)) / 2) + 1
        )  # This is your -R
        duration = int(test.window[:-1]) + 30
        window = str(duration) + "s"
        for i in range(2, int(test.scale_max) + 1):
            Requests = Requests + int(test.up_threshold)
            print(Requests)
            print(window)
            loader = subprocess.Popen(
                [
                    "wrk",
                    "-t1",
                    "-c1",
                    "-d" + window,
                    "-R" + str(Requests),
                    "http://" + service_address,
                ]
            )
            print("sleeping for" + str(duration - 10) + " seconds")
            time.sleep(duration - 10)
            stdin, stdout, stderr = ssh.exec_command(
                "sudo docker service ls -f name="
                + test.service_name
                + " --format {{.Replicas}}"
            )
            output = stdout.read().decode()
            print("Checking after scale")
            print(output)
            if len(output) == 0 or i != int(output.split("/")[0]):
                message += (
                    "Service did not scale to "
                    + str(i)
                    + " instances in the given time\n"
                )
                loader.wait()
            else:
                marks += 1
                message += (
                    "Service scaled to "
                    + str(i)
                    + " instances in the given time\n"
                )
            loader.wait()
            print(message)
            sub.message = message
            sub.faculty_message = faculty_message
            sub.marks = marks
            sub.save()


# def give_marks(testpassed, testname):
#     marks = 0
#     message = ""
#     if testpassed:
#         marks = 1
#         message += testname + " test passed\n\n"
#     else:
#         message += testname + " test failed\n\n"
#     return marks, message
