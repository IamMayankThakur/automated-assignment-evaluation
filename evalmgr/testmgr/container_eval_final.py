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

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username, key_filename=path_to_key)

    for test in tests:
        # test1 container name
        message += "---Container test running---\n"
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

        # test2 Container image
        stdin, stdout, stderr = ssh.exec_command("sudo docker ps --format '{{.Image}}'")
        output = stdout.read().decode()
        if test.container_image in output:
            message += "Container was run using " + test.container_image + " image\n"
            marks += 1
            message += "---Container test passed---\n"
        else:
            message += (
                "Container was not run using " + test.container_image + " image\n"
            )
            message += "---Container test failed---\n"

        # test3 ports exposed
        message += "---Ports test running---\n"
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
            message += "---Ports test passed---\n"
        else:
            message += "---Ports test failed---\n"

        # test4 networks created
        message += "---Network test running---\n"
        stdin, stdout, stderr = ssh.exec_command(
            "sudo docker network ls --format '{{.Name}}'"
        )
        output = stdout.read().decode()
        networks = test.networks.split(",")
        networkpresent = True
        for network in networks:
            if network in output:
                message += "Network " + network + " is created\n"
            else:
                message += "Network " + network + " is not created\n"
                networkpresent = False
        if networkpresent:
            marks += 1
            message += "---Network test passed---\n"
        else:
            message += "---Network test failed---\n"

        # test5 connected to networks
        message += "---Connected networks test running---\n"
        stdin, stdout, stderr = ssh.exec_command(
            "sudo docker inspect "
            + test.container_name
            + " --format '{{json .NetworkSettings.Networks}}'"
        )
        output = stdout.read().decode()
        container_networks = json.loads(output)
        required_networks = test.connected_to_networks.split(",")
        networkconnected = True
        for required_network in required_networks:
            if required_network in container_networks.keys():
                message += (
                    "Container "
                    + test.container_name
                    + " connected to "
                    + required_network
                    + "\n"
                )
            else:
                message += (
                    "Container "
                    + test.container_name
                    + " not connected to "
                    + required_network
                    + "\n"
                )
                networkconnected = False
        if networkconnected:
            message += "---Connected network tests passed---\n"
            marks += 1
        else:
            message += "---Conneced network tests failed---\n"

        # test6 env variables
        # message += "---Env variables test running---\n"
        # stdin, stdout, stderr = ssh.exec_command(
        #     "sudo docker exec " + test.container_name + " env"
        # )
        # output = stdout.read().decode()
        # container_env_variables = output.split("\n")
        # env_variables = test.env_variables.split("\n")
        # setcorrectly = True
        # for env_variable in env_variables:
        #     env_string = env_variable.replace(",", "=")
        #     # Because ENV_VARIABLE=test=sample is also a valid env variable, splitting on = might get messy
        #     # Hence total string comparison is done ("ENV_VARIABLE=test=sample" is compared)
        #     if env_string in container_env_variables:
        #         message += (
        #             "Variable "
        #             + env_variable.split(",", 1)[0]
        #             + " is set correctly as "
        #             + env_variable.split(",", 1)[1]
        #             + "\n"
        #         )
        #     else:
        #         message += (
        #             "Variable "
        #             + env_variable.split(",", 1)[0]
        #             + " is not set as "
        #             + env_variable.split(",", 1)[1]
        #             + "\n"
        #         )
        #         setcorrectly = False
        # if setcorrectly:
        #     marks += 1
        #     message += "---Env variables test passed---\n"
        # else:
        #     message += "---Env variables test failed---\n"
        # print(message)

        # test7 volumes

        # test7 commands

        # test8 num_cpus
