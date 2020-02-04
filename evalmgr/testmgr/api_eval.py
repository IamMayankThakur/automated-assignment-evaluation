import configparser
import json
import ast

import requests
from celery import shared_task


from facultymgr.models import Evaluation
from notifymgr.mail import send_mail
from studentmgr.models import Submission
from .models import ApiTestModel


@shared_task(time_limit=200)
def setup_api_eval(*args, **kwargs):
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
        api_test = ApiTestModel()
        api_test.sanity = True if c[s]['sanity'] == "True" else False
        api_test.api_endpoint = c[s]['api_endpoint']
        api_test.api_method = c[s]['api_method']
        api_test.api_message_body = c[s]['api_message_body']
        api_test.expected_status_code = c[s]['expected_status_code']
        api_test.expected_response_body = c[s]['expected_response_body']
        api_test.evaluation = Evaluation.objects.get(id=eval_id)
        api_test.save()


@shared_task(time_limit=200)
def do_api_eval(*args, **kwargs):
    sub_id = kwargs.get('sub_id', None)
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
    if response.status_code == test.expected_status_code:
        marks += (0.5 if test.expected_response_body != "" else 1)
        if test.expected_response_body != "":
            if json.loads(response.content) == ast.literal_eval(test.expected_response_body):
                marks += 0.5
    else:
        message += " " + test.api_endpoint + " failed " + " "
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
                response = requests.get(public_ip+test.api_endpoint)
                marks_for_test, message_for_test = give_marks(response, test)
                marks += marks_for_test
                message += message_for_test
            elif test.api_method == "POST":
                response = requests.post(public_ip+test.api_endpoint, data=ast.literal_eval(test.api_message_body))
                marks_for_test, message_for_test = give_marks(response, test)
                marks += marks_for_test
                message += message_for_test
            elif test.api_method == "PUT":
                response = requests.put(public_ip + test.api_endpoint, data=ast.literal_eval(test.api_message_body))
                marks_for_test, message_for_test = give_marks(response, test)
                marks += marks_for_test
                message += message_for_test
            elif test.api_method == "DELETE":
                response = requests.delete(public_ip + test.api_endpoint)
                marks_for_test, message_for_test = give_marks(response, test)
                marks += marks_for_test
                message += message_for_test
    except Exception as e:
        print("Error", e)
        return marks, message
    return marks, message


