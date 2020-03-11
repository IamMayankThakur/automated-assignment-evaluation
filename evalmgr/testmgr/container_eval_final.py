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
        container_test.connected_to_networks = c[s]["connected_to_networks"]
        container_test.env_variables = c[s]["env_variables"]
        container_test.volumes = c[s]["volumes"]
        container_test.commands = c[s]["commands"]
        container_test.num_cpus = c[s]["num_cpus"]
        container_test.evaluation = Evaluation.objects.get(id=eval_id)
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
    facultymessage = ""

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, username=username, key_filename=path_to_key)
    except Exception as e:
        print("ERROR: ", e)
        message += "Fatal Error.! Check if your instance is running / port is open / pem file is correct etc"
        sub.message = message
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
            containerdata = json.loads(output)[0]
            message += "Container name test passed\n\n"
            marks += 1

        except Exception as e:
            print("ERROR: ", e)
            message += (
                "Fatal Error: Container " + test.container_name + " not running\n"
            )
            facultymessage += (
                "Fatal Error: "
                + test.container_name
                + " container is not running\nStopping all tests\n"
            )
            sub.message = message
            sub.faculty_message = facultymessage
            sub.marks = marks
            sub.save()
            continue

        # test2 Container image
        message += "Container Image test running\n"
        testpassed = containerdata["Config"]["Image"] == test.container_image
        facultymessage += (
            "Container was not run using " + test.container_image + " image\n",
            "",
        )[testpassed]
        marksfortest, messagefortest = give_marks(testpassed, "Container Image")
        message += messagefortest
        marks += marksfortest

        # test3 port test
        message += "Ports test running\n"
        test_ports = test.ports_exposed.split(",")
        marksfortest, messagefortest, facultymessagefortest = port_test(
            test_ports, test, containerdata
        )
        message += messagefortest
        marks += marksfortest
        facultymessage += facultymessagefortest

        # test4 connected to networks test
        message += "Network connection test running\n"
        required_networks = test.connected_to_networks.split(",")
        marksfortest, messagefortest, facultymessagefortest = network_test(
            required_networks, test, containerdata
        )
        message += messagefortest
        marks += marksfortest
        facultymessage += facultymessagefortest

        # test5 env variables
        message += "Env variables test running\n"
        env_variables = test.env_variables.split("\n")
        marksfortest, messagefortest, facultymessagefortest = env_test(
            env_variables, test, containerdata
        )
        message += messagefortest
        marks += marksfortest
        facultymessage += facultymessagefortest

        # test6 volumes
        message += "Volumes test running\n"
        test_volumes = test.volumes.split(",")
        marksfortest, messagefortest, facultymessagefortest = volume_test(
            test_volumes, test, containerdata
        )
        message += messagefortest
        marks += marksfortest
        facultymessage += facultymessagefortest

        # test7 commands
        message += "Commands test running\n"
        commands = test.commands.split("\n")
        marksfortest, messagefortest, facultymessagefortest = command_test(
            commands, test, ssh
        )
        message += messagefortest
        marks += marksfortest
        facultymessage += facultymessagefortest

        # test8 num_cpus
        message += "CPU test running\n"
        marksfortest, messagefortest, facultymessagefortest = cpu_test(
            test.num_cpus, test, containerdata
        )
        message += messagefortest
        marks += marksfortest
        facultymessage += facultymessagefortest

        sub.marks = marks
        sub.facultymessage = facultymessage
        sub.message = message
        sub.save()


def cpu_test(num_cpus, test, containerdata):
    testpassed = (int(containerdata["HostConfig"]["NanoCpus"]) / 10 ** 9) == num_cpus
    facultymessage = ("Container is not using " + str(num_cpus) + " cpu(s)\n", "")[
        testpassed
    ]
    marks, message = give_marks(testpassed, "CPU")
    return marks, message, facultymessage


def network_test(required_networks, test, containerdata):
    testpassed = True
    facultymessage = ""
    for required_network in required_networks:
        try:
            containerdata["NetworkSettings"]["Networks"][required_network]
        except Exception:
            testpassed = False
            facultymessage = (
                "Container "
                + test.container_name
                + " is not connected to "
                + required_network
                + " network\n"
            )
            break
    marks, message = give_marks(testpassed, "Network Connection")
    return marks, message, facultymessage


def port_test(test_ports, test, containerdata):
    testpassed = False
    facultymessage = ""
    for port_map in test_ports:
        hostport, containerport = port_map.split(":", 1)
        if "/udp" not in containerport:
            containerport += "/tcp"
        try:
            testpassed = (
                containerdata["NetworkSettings"]["Ports"][containerport][0]["HostPort"]
                == hostport
            )

        except Exception:
            testpassed = False
            facultymessage = (
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
            facultymessage = (
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
    return marks, message, facultymessage


def env_test(env_variables, test, containerdata):
    testpassed = False
    facultymessage = ""
    for env_variable in env_variables:
        env_variable = env_variable.replace(",", "=", 1)
        testpassed = env_variable in containerdata["Config"]["Env"]
        if testpassed is False:
            facultymessage = (
                "Environment variable "
                + env_variable.split("=", 1)[0]
                + " not set or not set as "
                + env_variable.split("=", 1)[1]
                + "\n"
            )
            break
    marks, message = give_marks(testpassed, "Env variables")
    return marks, message, facultymessage


def volume_test(test_volumes, test, containerdata):
    testpassed = False
    facultymessage = ""
    for volume in test_volumes:
        try:
            testpassed = True in (
                containerdata["Mounts"][i]["Name"] == volume
                for i in range(len(containerdata["Mounts"]))
            )
        except Exception:
            testpassed = False
            facultymessage = (
                "Volume "
                + volume
                + " is not attachted to "
                + test.container_name
                + " container\n"
            )
            break
        if testpassed is False:
            facultymessage = (
                "Volume "
                + volume
                + " is not attachted to "
                + test.container_name
                + " container\n"
            )
            break
    marks, message = give_marks(testpassed, "Volumes")
    return marks, message, facultymessage


def command_test(commands, test, ssh):
    testpassed = True
    facultymessage = ""
    for command in commands:
        inp, errorexpected = command.split(":", 1)
        errorexpected = errorexpected == "True"
        if "sudo" not in inp:
            inp = "sudo " + inp
        stdin, stdout, stderr = ssh.exec_command(inp)
        errors = stderr.read().decode()
        if not errorexpected and len(errors.strip()) != 0:
            facultymessage += errors
            testpassed = False
        if errorexpected and len(errors.strip()) == 0:
            testpassed = False
            facultymessage += errors
    marks, message = give_marks(testpassed, "Commands")
    return marks, message, facultymessage


def give_marks(testpassed, testname):
    marks = 0
    message = ""
    if testpassed:
        marks = 1
        message += testname + " test passed\n\n"
    else:
        message += testname + " test failed\n\n"
    return marks, message
