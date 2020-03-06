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
        container_test.networks = c[s]["networks"]
        container_test.connected_to_networks = c[s]["connected_to_networks"]
        container_test.env_variables = c[s]["env_variables"]
        container_test.volumes = c[s]["volumes"]
        container_test.commands = c[s]["volumes"]
        container_test.num_cpus = c[s]["num_cpus"]
        container_test.evaluation = Evaluation.objects.get(id=eval_id)
        container_test.save()


# container_name = users
# container_image = alpine
# ports_exposed = 8080:8080,4567:4567
# networks = testnetwork,mynetwork
# connected_to_networks = testnetwork
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
    facultymessage = ""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username, key_filename=path_to_key)

    for test in tests:
        # test1 container name
        message += "Container test running\n"
        testpassed = False
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.Names}}'")
        output = stdout.read().decode()

        if test.container_name in output:
            testpassed = True

        marksfortest, messagefortest = give_marks(testpassed, "Container")
        message += messagefortest
        marks += marksfortest

        if not testpassed:
            message += "Fatal Error: Container not running\n"
            facultymessage += (
                "Fatal Error: "
                + test.container_name
                + " container is not running\nStopping all tests\n"
            )
            break

        # test2 Container image
        message += "Container Image test running\n"
        testpassed = False
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.Image}}'")
        output = stdout.read().decode()

        if test.container_image in output:
            testpassed = True
        else:
            facultymessage += (
                "Container was not run using " + test.container_image + " image\n"
            )

        marksfortest, messagefortest = give_marks(testpassed, "Container Image")
        message += messagefortest
        marks += marksfortest

        # test3 alternative approach
        message += "Ports test running\n"
        testpassed = True
        test_ports = test.ports_exposed.split(",")
        for port_map in test_ports:
            port = port_map.split(":")
            stdin, stdout, stderr = ssh.exec_command(
                "sudo docker port " + test.container_name + " " + port[1]
            )
            errormessage = stderr.read().decode().split(":")
            containerport = stdout.read().decode().split(":", 1)
            if errormessage[0] == "Error" or containerport[1].strip() != port[0]:
                facultymessage += (
                    "Port "
                    + port[1]
                    + " in "
                    + test.container_name
                    + " container not mapped to port "
                    + port[0]
                    + " of host\n"
                )
                testpassed = False

        marksfortest, messagefortest = give_marks(testpassed, "Ports")
        message += messagefortest
        marks += marksfortest

        # test4 networks created
        message += "Network test running\n"
        testpassed = True
        networks = test.networks.split(",")
        for network in networks:
            stdin, stdout, stderr = ssh.exec_command(
                "sudo docker network inspect " + network
            )
            errormessage = stderr.read().decode()
            if len(errormessage) != 0:
                facultymessage += "Network " + network + " is not created\n"
                testpassed = False
        marksfortest, messagefortest = give_marks(testpassed, "Network")
        marks += marksfortest
        message += messagefortest

        # test5 connected to networks
        message += "Network connection test running\n"
        testpassed = True
        required_networks = test.connected_to_networks.split(",")

        for required_network in required_networks:
            stdin, stdout, stderr = ssh.exec_command(
                "sudo docker inspect "
                + test.container_name
                + " --format '{{json .NetworkSettings.Networks."
                + required_network
                + "}}'"
            )
            output = stdout.read().decode()
            if output.strip() == "null":
                facultymessage += (
                    "Network "
                    + required_network
                    + " is not connected to "
                    + test.container_name
                    + " container\n"
                )
                testpassed = False
        marksfortest, messagefortest = give_marks(testpassed, "Network connection")
        marks += marksfortest
        message += messagefortest

        # test6 env variables
        message += "Env variables test running\n"
        testpassed = True
        env_variables = test.env_variables.split("\n")
        for env_variable in env_variables:
            env_var, env_value = env_variable.split(",", 1)
            stdin, stdout, stderr = ssh.exec_command(
                "sudo docker exec " + test.container_name + " env printenv " + env_var
            )
            container_value = stdout.read().decode().strip()
            if container_value != env_value:
                facultymessage += (
                    "Environment variable "
                    + env_variable
                    + " not set or not set as "
                    + env_value
                    + "\n"
                )
                testpassed = False
        marksfortest, messagefortest = give_marks(testpassed, "Env variables")
        marks += marksfortest
        message += messagefortest

        # test7 volumes

        # test8 commands

        # test9 num_cpus


def give_marks(testpassed, testname):
    marks = 0
    message = ""
    if testpassed:
        marks = 1
        message += testname + " test passed\n\n"
    else:
        message += testname + " test failed\n\n"
    return marks, message
