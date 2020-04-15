import configparser
import json
import ast
import paramiko
import requests
import socket

# import requests
from celery import shared_task

from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission
from .models import ApiTestModel
from .models import ContainerTestModel
from paramiko.ssh_exception import (
    BadHostKeyException,
    AuthenticationException,
    SSHException,
)


@shared_task(time_limit=100)
def setup_container_eval(*args, **kwargs):
    eval_id = (
        kwargs["form_data"]["eval_id"] if "eval_id" in kwargs["form_data"] else None
    )
    if eval_id is None:
        raise RuntimeError
    container_test = ContainerTestModel()
    container_test.container_name = kwargs["form_data"]["container_name"]
    container_test.container_image = kwargs["form_data"]["container_image"]
    container_test.ports_exposed = kwargs["form_data"]["ports_exposed"]
    container_test.connected_to_networks = kwargs["form_data"]["networks"]
    container_test.env_variables = kwargs["form_data"]["env_variables"]
    container_test.volumes = kwargs["form_data"]["volumes"]
    container_test.commands = kwargs["form_data"]["commands"]
    container_test.num_cpus = kwargs["form_data"]["cpus"]
    container_test.evaluation = Evaluation.objects.get(
        id=int(kwargs["form_data"]["eval_id"])
    )
    container_test.save()


@shared_task(time_limit=200)
def do_container_eval(*args, **kwargs):
    sub = Submission.objects.get(id=kwargs.get("sub_id"))
    ip = sub.public_ip_address
    username = sub.username
    path_to_key = sub.private_key_file.path
    tests = ContainerTestModel.objects.filter(evaluation=sub.evaluation)
    marks = 0
    message = ""
    faculty_message = ""

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

        # test1 container name
        message += "Container name test running\n"
        try:
            stdin, stdout, stderr = ssh.exec_command(
                "sudo docker inspect " + test.container_name
            )
            output = stdout.read().decode()
            container_data = json.loads(output)[0]
            message += "Container name test passed\n\n"
            marks += 1

        except (json.JSONDecodeError, IndexError):
            message += (
                "Fatal Error: Container " + test.container_name + " not running\n"
            )
            faculty_message += (
                "Fatal Error: "
                + test.container_name
                + " container is not running\nStopping all tests\n"
            )
            sub.message = message
            sub.faculty_message = faculty_message
            sub.marks = marks
            sub.save()
            continue

        # test2 Container image
        message += "Container Image test running\n"
        testpassed = container_data["Config"]["Image"] == test.container_image
        faculty_message += (
            "Container was not run using " + test.container_image + " image\n",
            "",
        )[testpassed]
        marks_for_test, message_for_test = give_marks(testpassed, "Container Image")
        message += message_for_test
        marks += marks_for_test

        # test3 port test
        message += "Ports test running\n"
        test_ports = test.ports_exposed.split(",")
        marks_for_test, message_for_test, faculty_message_for_test = port_test(
            test_ports, test, container_data
        )
        message += message_for_test
        marks += marks_for_test
        faculty_message += faculty_message_for_test

        # test4 connected to networks test
        message += "Network connection test running\n"
        required_networks = test.connected_to_networks.split(",")
        marks_for_test, message_for_test, faculty_message_for_test = network_test(
            required_networks, test, container_data
        )
        message += message_for_test
        marks += marks_for_test
        faculty_message += faculty_message_for_test

        # test5 env variables
        message += "Env variables test running\n"
        env_variables = test.env_variables.split("\n")
        marks_for_test, message_for_test, faculty_message_for_test = env_test(
            env_variables, test, container_data
        )
        message += message_for_test
        marks += marks_for_test
        faculty_message += faculty_message_for_test

        # test6 volumes
        message += "Volumes test running\n"
        test_volumes = test.volumes.split(",")
        marks_for_test, message_for_test, faculty_message_for_test = volume_test(
            test_volumes, test, container_data
        )
        message += message_for_test
        marks += marks_for_test
        faculty_message += faculty_message_for_test

        # test7 commands
        message += "Commands test running\n"
        commands = test.commands.split("\n")
        marks_for_test, message_for_test, faculty_message_for_test = command_test(
            commands, test, ssh
        )
        message += message_for_test
        marks += marks_for_test
        faculty_message += faculty_message_for_test

        # test8 num_cpus
        message += "CPU test running\n"
        marks_for_test, message_for_test, faculty_message_for_test = cpu_test(
            test.num_cpus, test, container_data
        )
        message += message_for_test
        marks += marks_for_test
        faculty_message += faculty_message_for_test

    sub.marks = marks
    sub.faculty_message = faculty_message
    print(faculty_message)
    sub.message = message
    sub.save()


def cpu_test(num_cpus, test, container_data):
    testpassed = (int(container_data["HostConfig"]["NanoCpus"]) / 10 ** 9) == num_cpus
    faculty_message = ("Container is not using " + str(num_cpus) + " cpu(s)\n", "")[
        testpassed
    ]
    marks, message = give_marks(testpassed, "CPU")
    return marks, message, faculty_message


def network_test(required_networks, test, container_data):
    testpassed = True
    faculty_message = ""
    for required_network in required_networks:
        try:
            container_data["NetworkSettings"]["Networks"][required_network]
        except (IndexError, KeyError):
            testpassed = False
            faculty_message = (
                "Container "
                + test.container_name
                + " is not connected to "
                + required_network
                + " network\n"
            )
            break
    marks, message = give_marks(testpassed, "Network Connection")
    return marks, message, faculty_message


def port_test(test_ports, test, container_data):
    testpassed = False
    faculty_message = ""
    for port_map in test_ports:
        hostport, containerport = port_map.split(":", 1)
        if "/udp" not in containerport:
            containerport += "/tcp"
        try:
            testpassed = (
                container_data["NetworkSettings"]["Ports"][containerport][0]["HostPort"]
                == hostport
            )

        except (IndexError, KeyError):
            testpassed = False
            faculty_message = (
                "Port "
                + containerport
                + " in "
                + test.container_name
                + " container not mapped to port "
                + hostport
                + " of host\n"
            )
            break
        if testpassed is False:
            faculty_message = (
                "Port "
                + containerport
                + " in "
                + test.container_name
                + " container not mapped to port "
                + hostport
                + " of host\n"
            )
            break
    marks, message = give_marks(testpassed, "Ports")
    return marks, message, faculty_message


def env_test(env_variables, test, container_data):
    testpassed = False
    faculty_message = ""
    for env_variable in env_variables:
        env_variable = env_variable.replace(",", "=", 1).strip()
        testpassed = env_variable in (
            x.strip() for x in container_data["Config"]["Env"]
        )
        if testpassed is False:
            faculty_message = (
                "Environment variable "
                + env_variable.split("=", 1)[0]
                + " not set or not set as "
                + env_variable.split("=", 1)[1]
                + "\n"
            )
            break
    marks, message = give_marks(testpassed, "Env variables")
    return marks, message, faculty_message


def volume_test(test_volumes, test, container_data):
    testpassed = False
    faculty_message = ""
    for volume in test_volumes:
        try:
            testpassed = True in (
                container_data["Mounts"][i]["Name"] == volume
                for i in range(len(container_data["Mounts"]))
            )
        except (KeyError, IndexError):
            testpassed = False
            faculty_message = (
                "Volume "
                + volume
                + " is not attachted to "
                + test.container_name
                + " container\n"
            )
            break
        if testpassed is False:
            faculty_message = (
                "Volume "
                + volume
                + " is not attachted to "
                + test.container_name
                + " container\n"
            )
            break
    marks, message = give_marks(testpassed, "Volumes")
    return marks, message, faculty_message


def command_test(commands, test, ssh):
    testpassed = True
    faculty_message = ""
    for command in commands:
        inp, errorexpected = command.split(":", 1)
        errorexpected = errorexpected == "True"
        if "sudo" not in inp:
            inp = "sudo " + inp
        stdin, stdout, stderr = ssh.exec_command(inp)
        errors = stderr.read().decode()
        if not errorexpected and len(errors.strip()) != 0:
            faculty_message += errors
            testpassed = False
        if errorexpected and len(errors.strip()) == 0:
            testpassed = False
            faculty_message += errors
    marks, message = give_marks(testpassed, "Commands")
    return marks, message, faculty_message


def give_marks(testpassed, testname):
    marks = 0
    message = ""
    if testpassed:
        marks = 1
        message += testname + " test passed\n\n"
    else:
        message += testname + " test failed\n\n"
    return marks, message
