import configparser
import json
import ast
import random
import string
import time

import paramiko
import requests
from celery import shared_task

from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission, SubmissionAssignment3
from .models import ApiTestModel


@shared_task(time_limit=200)
def setup_api_eval(*args, **kwargs):
    eval_id = kwargs["eval_id"] if "eval_id" in kwargs else None
    if eval_id is None:
        raise RuntimeError
    evaluation = Evaluation.objects.get(pk=eval_id)
    file = evaluation.conf_file.path
    c = configparser.ConfigParser()
    c.read(file)
    sections = c.sections()
    print(sections)
    sections.remove("Settings")
    for s in sections:
        api_test = ApiTestModel()
        api_test.test_name = s
        api_test.sanity = True if c[s]["sanity"] == "True" else False
        api_test.api_endpoint = c[s]["api_endpoint"]
        api_test.api_method = c[s]["api_method"]
        api_test.api_message_body = c[s]["api_message_body"]
        api_test.expected_status_code = c[s]["expected_status_code"]
        api_test.expected_response_body = c[s]["expected_response_body"]
        api_test.evaluation = Evaluation.objects.get(id=eval_id)
        api_test.save()


@shared_task(time_limit=200)
def do_api_eval(*args, **kwargs):
    sub_id = kwargs.get("sub_id", None)
    if sub_id is None:
        raise RuntimeError
    submission = Submission.objects.get(id=sub_id)
    public_ip = submission.public_ip_address
    sanity_tests = ApiTestModel.objects.filter(sanity=True)
    normal_tests = ApiTestModel.objects.filter(sanity=False)
    marks_sanity, message_sanity = run_tests(sanity_tests, public_ip)
    if marks_sanity == 0:
        message_sanity += " Sanity Test Failed. Hence further tests not evaluated. "
        submission.marks = 0
        submission.message = message_sanity
        submission.save()
        return
    marks, message = run_tests(normal_tests, public_ip)
    submission.marks = marks
    submission.message = message
    submission.save()
    # send_mail(sub_id)
    return


def give_marks(response, test):
    marks = 0
    message = ""
    if response.status_code == int(test.expected_status_code):
        marks += 0.5 if test.expected_response_body != "" else 1
        if test.expected_response_body != "":
            if (
                ast.literal_eval(test.expected_response_body).items()
                <= json.loads(response.content).items()
            ):
                marks += 0.5
    else:
        message += " " + test.test_name + " failed " + " "
    return marks, message


def run_tests(test_objects, public_ip):
    marks = 0
    message = ""
    # import pdb
    # pdb.set_trace()
    if public_ip.count(":") > 1:
        message += " Marks reduced as API not on port 80  "
    else:
        marks += 1
        message += "  Running on port 80  "
    try:
        for test in test_objects:
            if test.api_method == "GET":
                response = requests.get(public_ip + test.api_endpoint)
                marks_for_test, message_for_test = give_marks(response, test)
                marks += marks_for_test
                message += message_for_test
            elif test.api_method == "POST":
                response = requests.post(
                    public_ip + test.api_endpoint,
                    data=ast.literal_eval(test.api_message_body),
                )
                marks_for_test, message_for_test = give_marks(response, test)
                marks += marks_for_test
                message += message_for_test
            elif test.api_method == "PUT":
                response = requests.put(
                    public_ip + test.api_endpoint,
                    data=ast.literal_eval(test.api_message_body),
                )
                marks_for_test, message_for_test = give_marks(response, test)
                marks += marks_for_test
                message += message_for_test
            elif test.api_method == "DELETE":
                response = requests.delete(public_ip + test.api_endpoint)
                marks_for_test, message_for_test = give_marks(response, test)
                marks += marks_for_test
                message += message_for_test
            print("ENDPOINT", public_ip + test.api_endpoint)
            print("RESPONSE ", response)
            print("MARKS FOR TEST", marks_for_test)
        print("MARKS, MESSAGE", marks, message)
        return marks, message
    except Exception as e:
        print("Error", e)
        return marks, message


@shared_task(time_limit=300)
def do_api_eval_cc(*args, **kwargs):
    try:
        marks = 0
        message = ""
        sub_id = kwargs.get("sub_id", None)
        if sub_id is None:
            print("No sub id")
            raise RuntimeError
        submission = Submission.objects.get(id=sub_id)
        public_ip = submission.public_ip_address

        if public_ip.count(":") > 1:
            message += " Not running on port 80 "
        else:
            marks += 1
            message += "Running on port 80"

        r = requests.put(
            public_ip + "/api/v1/users",
            json={
                "username": "userName",
                "password": "3d725109c7e7c0bfb9d709836735b56d943d263f",
            },
        )
        if r.status_code == 201:
            marks += 1
            message += " Passed Add user "
            print(" Passed Add user ")
        else:
            message += " Failed Add user "
            print(" Failed Add user ")

        r = requests.post(
            public_ip + "/api/v1/rides",
            json={
                "created_by": "userName",
                "timestamp": "21-08-2021:00-00-00",
                "source": "1",
                "destination": "2",
            },
        )
        if r.status_code == 201:
            marks += 1
            message += " Passed Create new ride "
            print(" Passed Create new ride ")
        else:
            message += " Failed Failed create new ride "
            print(" Failed Add ride ")

        r = requests.get(public_ip + "/api/v1/rides?source=1&destination=2")
        if r.status_code == 200:
            try:
                ride_id = str(json.loads(r.content)[0]["rideId"])
                message += " Passed get upcoming ride for source and destination "
                marks += 1
                print(" Passed get upcoming ride for source and destination ")
            except Exception as e:
                print("Cant get rideid ", e)
                message += " Failed to get ride id. Further tests not evaluated "
                submission.marks = marks
                submission.message = message
                submission.save()
                return
        else:
            message += " Failed get upcoming ride for source and destination "
            message += " Failed to get ride id. Further tests not evaluated "
            submission.marks = marks
            submission.message = message
            submission.save()
            return

        r = requests.get(public_ip + "/api/v1/rides/" + ride_id)
        if r.status_code == 200:
            marks += 1
            message += " Passed Get details for ride "
            print(" Passed Get details for ride ")
        else:
            message += " Failed Get details for given ride "
            print(" Failed Get details for given ride ")

        r = requests.delete(public_ip + "/api/v1/rides/" + ride_id)
        if r.status_code == 200:
            marks += 1
            message += " Passed delete ride "
            print(" Passed delete ride ")
        else:
            message += " Failed delete ride "
            print(" Failed delete ride ")

        r = requests.delete(public_ip + "/api/v1/users/userName")
        if r.status_code == 200:
            marks += 1
            message += " Passed delete user "
            print(" Passed delete user ")
        else:
            message += " Failed delete user "
            print(" Failed delete user ")

        r = requests.delete(public_ip + "/api/v1/users/wrongUser")
        if r.status_code == 400:
            marks += 1
            message += " Passed delete user "
            print(" Passed delete user ")
        else:
            message += " Failed delete user "
            print(" Failed delete user ")

        r = requests.get(public_ip + "/api/v1/rides?source=34&destination=11")
        if r.status_code == 204:
            marks += 1
            message += " Passed GetUpcomingRides "
            print(" Passed GetUpcomingRides ")
        else:
            message += " Failed GetUpcomingRides "
            print(" Failed GetUpcomingRides ")

        submission.marks = marks * 0.6
        submission.message = message
        submission.save()
        return
    except Exception as e:
        submission.marks += 0
        submission.message += "Fatal Error"
        submission.save()
        print(e)
        return


def random_name():
    return "".join(random.choice(string.ascii_lowercase) for i in range(10))


@shared_task(time_limit=600)
def do_assignment_3_eval(*args, **kwargs):
    try:
        marks = 0
        message = ""
        sub_id = kwargs.get("sub_id", None)
        if sub_id is None:
            print("No sub id")
            raise RuntimeError
        submission = SubmissionAssignment3.objects.get(id=sub_id)
        password = "3d725109c7e7c0bfb9d709836735b56d943d263f"
        lb_ip = submission.lb_ip
        users_ip = submission.users_ip
        rides_ip = submission.rides_ip

        r_users = requests.get(users_ip + "/api/v1/_count")
        r_rides = requests.get(rides_ip + "/api/v1/_count")
        if "0" in str(r_users.content) and "0" in str(r_rides.content):
            marks += 0.5
            message += (
                " Count initialized to 0 on either users and rides microservice. "
            )
        else:
            message += (
                " Count not initialized to 0 on either users or rides microservice. "
            )
            submission.marks = marks
            submission.message = message
            submission.save()
            return

        r1 = requests.put(
            lb_ip + "/api/v1/users",
            json={
                "username": "userName",
                "password": "3d725109c7e7c0bfb9d709836735b56d943d263f",
            },
        )

        r2 = requests.post(
            lb_ip + "/api/v1/rides",
            json={
                "created_by": "userName",
                "timestamp": "21-08-2021:00-00-00",
                "source": "1",
                "destination": "2",
            },
        )

        if r1.status_code == 201 and r2.status_code == 201:
            marks += 1
            message += " Load Balancer working. "
        else:
            message += " Load Balancer not working. "
            submission.marks = marks
            submission.message = message
            submission.save()
            return

        r_users = requests.delete(users_ip + "/api/v1/_count")
        r_rides = requests.delete(rides_ip + "/api/v1/_count")

        if r_rides.status_code == 200 and r_users.status_code == 200:
            message += " Reset count API returning 200 HTTP response. "
        else:
            message += " Reset count API not returning 200 HTTP response. "
            submission.marks = marks
            submission.message = message
            submission.save()
            return

        r_users = requests.get(users_ip + "/api/v1/_count")
        r_rides = requests.get(rides_ip + "/api/v1/_count")
        if "0" in str(r_users.content) and "0" in str(r_rides.content):
            marks += 0.5
            message += " Count successfully reset to 0. "
        else:
            message += " Count not reset to 0. "
            return

        requests.post(users_ip + "/api/v1/db/clear")
        requests.post(rides_ip + "/api/v1/db/clear")

        rand_users_correct = random.randrange(200, 400)
        rand_users_wrong = random.randrange(300, 500)

        rand_rides_correct = random.randrange(250, 500)
        rand_rides_wrong = random.randrange(100, 400)

        requests.put(
            lb_ip + "/api/v1/users",
            json={
                "username": "userName",
                "password": "3d725109c7e7c0bfb9d709836735b56d943d263f",
            },
        )

        for _ in range(rand_users_correct):
            name = random_name()
            requests.put(
                lb_ip + "/api/v1/users", json={"username": name, "password": password,},
            )

        for _ in range(rand_rides_correct):
            requests.post(
                lb_ip + "/api/v1/rides",
                json={
                    "created_by": "userName",
                    "timestamp": "21-08-2021:00-00-00",
                    "source": "1",
                    "destination": "2",
                },
            )

        count_rides = requests.get(lb_ip + "/api/v1/rides/count")
        if str(rand_rides_correct) in str(count_rides.content):
            marks += 0.5
            message += " Correct Ride Count Returned. "
        else:
            message += " Incorrect Ride Count Returned. "
            submission.marks = marks
            submission.message = message
            submission.save()
            return

        for _ in range(rand_users_wrong):
            name = random_name()
            requests.post(
                lb_ip + "/api/v1/users", json={"username": name, "password": password,},
            )

        for _ in range(rand_rides_wrong):
            requests.put(
                lb_ip + "/api/v1/rides",
                json={
                    "created_by": "userName",
                    "timestamp": "21-08-2021:00-00-00",
                    "source": "1",
                    "destination": "2",
                },
            )

        for _ in range(rand_rides_wrong):
            requests.get(lb_ip + "/api/v1/rides?source=1&destination=2")

        expected_users_count = str(
            rand_users_correct + rand_users_wrong + rand_rides_correct + 1
        )
        expected_rides_count = str(
            rand_rides_correct + rand_rides_wrong + 1 + rand_rides_wrong
        )

        r_users = requests.get(users_ip + "/api/v1/_count")
        r_rides = requests.get(rides_ip + "/api/v1/_count")
        if expected_users_count in str(r_users.content) and expected_rides_count in str(
            r_rides.content
        ):
            marks += 0.5
            message += " Count API returned correct count. "
        else:
            message += (
                " Count API did not return correct count. "
                + " Returned "
                + str(r_users.content)
                + " for users and "
                + str(r_rides.content)
                + " for rides. "
            )
            submission.marks = marks
            submission.message = message
            submission.save()
            return

        submission.marks = marks
        submission.message = message
        submission.save()

        requests.delete(users_ip + "/api/v1/_count")
        requests.delete(rides_ip + "/api/v1/_count")
        requests.post(users_ip + "/api/v1/db/clear")
        requests.post(rides_ip + "/api/v1/db/clear")

    except Exception as e:
        print(e)
        submission.marks = marks
        submission.message += (
            " Unknown Error. Ensure your instance is running and APIs are reachable. "
        )
        submission.save()


def count_container(ip, username, key_filename):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip[7:], username=username, key_filename=key_filename)
    stdin, stdout, stderr = ssh.exec_command(
        "sudo docker ps --format '{{.ID}} {{.Image}}' | grep rabbitmq | cut -d ' ' -f 1"
    )
    rabbitmq = str(stdout.read().decode())
    stdin, stdout, stderr = ssh.exec_command(
        "sudo docker ps --format '{{.ID}} {{.Image}}' | grep zookeeper | cut -d ' ' -f 1"
    )
    zookeeper = str(stdout.read().decode())
    stdin, stdout, stderr = ssh.exec_command("sudo docker ps | wc -l")
    output = stdout.read().decode()
    res = int(output) - 1
    return res, rabbitmq, zookeeper


@shared_task(time_limit=700)
def do_final_project_eval(sub_id, users_ip, rides_ip, lb_ip):
    marks = 0
    message = ""

    submission = Submission.objects.get(id=sub_id)
    orch_ip = submission.public_ip_address
    username = submission.username
    path_to_key = submission.private_key_file.path

    # 0. Clear db
    try:
        requests.post(orch_ip + "/api/v1/db/clear")
        print("Clear db done")
        message += "DB Clear Success. "
    except Exception as e:
        message += "DB Clear Failed. "
        submission.marks = marks
        submission.message = message
        submission.save()
        print(e)
        return

    # 1. SSH And count containers
    try:
        initial_container_count, rabbitmq, zookeeper = count_container(orch_ip, username, path_to_key)
        if rabbitmq == "" and rabbitmq == "":
            message += "Rabbitmq and zookeeper not running. "
            submission.message = message
            submission.marks = marks
            submission.save()
        message += "Initial container count is " + str(initial_container_count) + ". "
        print("Container Count Done")
    except Exception as e:
        print(e)
        message += " Failed to SSH, check your ip and private key "
        submission.marks = marks
        submission.message = message
        submission.save()
        return

    # 2. Create 1 user and 1 ride
    r1 = requests.put(
        lb_ip + "/api/v1/users",
        json={
            "username": "userName",
            "password": "3d725109c7e7c0bfb9d709836735b56d943d263f",
        },
    )

    r2 = requests.post(
        lb_ip + "/api/v1/rides",
        json={
            "created_by": "userName",
            "timestamp": "21-08-2021:00-00-00",
            "source": "1",
            "destination": "2",
        },
    )
    print("Created user and ride")

    if r1.status_code == 201 and r2.status_code == 201:
        marks += 1
        message += " Load Balancer working. "
        submission.marks = marks
        submission.message = message
        submission.save()
    else:
        message += " Load Balancer not working. "
        submission.marks = marks
        submission.message = message
        submission.save()
        return

    # 3. Sleep for 120 seconds
    time.sleep(120)
    try:
        r = requests.get(orch_ip + "/api/v1/worker/list")
        worker_list = r.json()
        print("Called worker list before auto scale", worker_list)
    except Exception as e:
        print(e)
        message += " Worker List API failed. "
        submission.message = message
        submission.marks = marks
        submission.save()

    # 4. Get users and rides 25-30 times
    _iterations = random.randrange(13, 15)
    for _ in range(_iterations):
        r = requests.get(lb_ip + "/api/v1/rides?source=1&destination=2")
        if r.status_code != 200:
            message += " Could not retrieve ride information. "
            submission.message = message
            submission.marks = marks
            submission.save()
            return

        r = requests.get(lb_ip + "/api/v1/rides?source=12&destination=21")
        if r.status_code != 204:
            message += " Inconsistent ride information. "
            submission.message = message
            submission.marks = marks
            submission.save()
            return

    marks += 1
    message += " DB get APIs successfully called"
    submission.marks = marks
    submission.message = message
    submission.save()
    print("DB get APIs called succesfully")

    # 5. Sleep for 2 mins 30 seconds
    time.sleep(160)

    # 6. Count Containers
    r = requests.get(orch_ip + "/api/v1/worker/list")
    worker_list = r.json()
    print("Called worker list after auto scale", worker_list)
    final_container_count, rmq, zk = count_container(orch_ip, username, path_to_key)
    print("Got final container count")
    if final_container_count > initial_container_count:
        marks += 2
        message += (
            " Auto scale successful, final container count is "
            + str(final_container_count)
            + ". "
        )
        submission.marks = marks
        submission.message = message
        submission.save()
    else:
        message += (
            " Auto scale failed, as final container count is "
            + str(final_container_count)
            + ". "
        )
        submission.marks = marks
        submission.message = message
        submission.save()

    # 7. Call workers list API
    time.sleep(150)
    try:
        r = requests.get(orch_ip + "/api/v1/worker/list")
        worker_list = r.json()
        print("Called worjer list ", worker_list)
        message += " Successfully retrieved workers list. "
        marks += 1
        submission.marks = marks
        submission.message = message
        submission.save()
    except Exception as e:
        print(e)
        message += " Could not retrieve workers. "
        submission.message = message
        submission.marks = marks
        submission.save()
        return

    # 8. Crash slave
    r = requests.post(orch_ip + "/api/v1/crash/slave")
    print("Crash slave called")
    if r.status_code == 200:
        message += " Crash slave API successfully returned 200 OK. "
        marks += 1
        submission.marks = marks
        submission.message = message
        submission.save()
    else:
        message += " Crash API did not return 200 OK. "
        submission.message = message
        submission.marks = marks
        submission.save()
        return

    # 9. Sleep for 1 min
    time.sleep(60)

    # 10. Ensure new slave is running
    r = requests.get(orch_ip + "/api/v1/worker/list")
    new_worker_list = r.json()
    print("Called worker list ", new_worker_list)
    marks += 1
    message += "Called worker list after new slave is spawned"
    if len(new_worker_list) == len(worker_list):
        message += " New worker started. "
        marks += 1
        if worker_list[len(worker_list) - 1] not in new_worker_list:
            message += " Old slave worker stopped. "
            marks += 1

    else:
        message += (
            " New slave not started. New PID not returned in worker list API call"
        )
        submission.message = message
        submission.marks = marks
        submission.save()
        return

    # 11. Get users and rides
    _iterations = random.randrange(3, 8)
    for _ in range(_iterations):
        r = requests.get(lb_ip + "/api/v1/rides?source=1&destination=2")
        if r.status_code != 200:
            message += " Could not retrive ride information after new slave creation. "
            submission.message = message
            submission.marks = marks
            submission.save()
            return

        r = requests.get(lb_ip + "/api/v1/rides?source=34&destination=23")
        if r.status_code != 204:
            message += " Inconsistent ride information after new slave creation"
            submission.message = message
            submission.marks = marks
            submission.save()
            return

    marks += 1
    message += " DB get APIs successfully called after new slave creation"

    # Save marks in the db
    submission.marks = marks
    submission.message = message
    submission.save()

    # 12. Clear db
    requests.post(orch_ip + "/api/v1/db/clear")
    print("Done")

    return
