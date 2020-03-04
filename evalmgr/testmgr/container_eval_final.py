import configparser
import json
import ast
import paramiko
import requests

import requests
from celery import shared_task

from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission
from .models import ApiTestModel
from .models import ContainerTestModel

@shared_task(time_limit=200)
def setup_container_eval(*args, **kwargs):
    eval_id = kwargs['eval_id'] if 'eval_id' in kwargs else None
    if eval_id is None:
        raise RuntimeError
    evaluation = Evaluation.objects.get(pk=eval_id)
    file = evaluation.conf_file.path
    c = configparser.ConfigParser()
    c.read(file)
    sections = c.sections()
    sections.remove('Settings')
    for s in sections:
        container_test = ContainerTestModel()
        container_test.test_name = s
        container_test.container_name = c[s]['container_name']
        container_test.container_image = c[s]['container_image']
        container_test.ports_exposed = c[s]['ports_exposed']
        container_test.network = c[s]['network']
        container_test.env_variables = c[s]['env_variables']
        container_test.volumes = c[s]['volumes']
        container_test.commands = c[s]['volumes']
        container_test.num_cpus = c[s]['num_cpus']
        container_test.evaluation = Evaluation.objects.get(id=eval_id)
        container_test.save()

@shared_task(time_limit=200)
def do_container_eval(*args,**kwargs):
    sub = Submission.objects.get(id=kwargs.get('sub_id'))
    ip = sub.public_ip_address
    username = sub.username
    marks = 0
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, username=username)
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.Image}}'")
        output = stdout.read().decode()
        print("==============================")
        print(output)
        print("==============================")
    except Exception as e:
        print("ERROR: ", e)
        marks += 0
        message += "Fatal Error.! Check if your instance is running / port is open / pem file is correct etc"
        sub.message = message
        sub.marks = marks
        sub.save()


