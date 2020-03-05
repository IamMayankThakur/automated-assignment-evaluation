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
from .models import ApiTestModel
from .models import ContainerTestModel


@shared_task(time_limit=200)
def setup_container_eval(*args, **kwargs):
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
        container_test = ContainerTestModel()
        container_test.test_name = s
        container_test.container_name = c[s]["container_name"]
        container_test.container_image = c[s]["container_image"]
        container_test.ports_exposed = c[s]["ports_exposed"]
        container_test.network = c[s]["network"]
        container_test.env_variables = c[s]["env_variables"]
        container_test.volumes = c[s]["volumes"]
        container_test.commands = c[s]["volumes"]
        container_test.num_cpus = c[s]["num_cpus"]
        container_test.evaluation = Evaluation.objects.get(id=eval_id)
        container_test.save()


# container_name = users
# container_image = alpine
# ports_exposed = 8080:8080,4567:4567
# network = testnetwork,mynetwork
# env_variables = TEAM_NAME,value
#     DATA,testdata
#     VAL,testval
# volumes = shared-data,personal-data
# commands = sleep 3, echo all done
# num_cpus = 1


@shared_task(time_limit=200)
def do_container_eval(*args, **kwargs):
    sub = Submission.objects.get(id=kwargs.get("sub_id"))
    ip = sub.public_ip_address
    username = sub.username
    path_to_key = sub.private_key_file.path
    tests = ContainerTestModel.objects.filter(evaluation=sub.evaluation)
    marks = 0
    message = ""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username, key_filename=path_to_key)

    for test in tests:
        # test1 container name
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.Names}}'")
        output = stdout.read().decode()
        print(output)
        print(test.container_name)
        if test.container_name in output:
            message += test.container_name + " container is running\n"
            marks += 1
        else:
            message += test.container_name + " container is not running\n"
            break

        # test3 ports exposed
        stdin, stdout, stderr = ssh.exec_command(
            "sudo docker port " + test.container_name
        )
        output = stdout.read().decode()
        container_ports = output.split("\n")
        container_ports = list(filter(lambda x: x != "", container_ports))

        test_ports = test.ports_exposed.split(",")
        for port_map in test_ports:
            port = port_map.split(":")
            if "/udp" not in port[1]:
                port[1] += "/tcp"
            portfound = False
            for container_port_map in container_ports:
                container_port = container_port_map.split("->")
                container_port = [x.strip() for x in container_port]
                if (
                    container_port[0] == port[1]
                    and container_port[1].split(":")[1] == port[0]
                ):
                    message += (
                        "Port "
                        + port[1]
                        + " in container mapped to port "
                        + port[0]
                        + " of host\n"
                    )
                    portfound = True
                    break
            if not portfound:
                message += (
                    "Port "
                    + port[1]
                    + " in container not mapped to port "
                    + port[0]
                    + " of host\n"
                )
                break
        if portfound is True:
            marks += 1
            message += "All required ports are mapped\n"
        print("===============FINAL OUTPUT================")
        print(message)
        print(marks)
        print("===============FINAL OUTPUT================")

        # test4 network

        # test5 env variables

        # test6 volumes

        # test7 commands

        # test8 num_cpus
