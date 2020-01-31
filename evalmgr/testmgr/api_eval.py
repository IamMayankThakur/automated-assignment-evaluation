import configparser
import requests

from .models import ApiTestModel
from ..facultymgr.models import Evaluation
from ..studentmgr.models import Submission


def setup_api_eval(*args, **kwargs):
    eval_id = kwargs['eval_id'] if 'eval_id' in kwargs else None
    if eval_id is None:
        raise RuntimeError
    evaluation = Evaluation.objects.get(pk=eval_id)
    file = evaluation.path
    c = configparser.ConfigParser()
    c.read(file)
    sections = c.sections().remove('Settings')
    for s in sections:
        api_test = ApiTestModel()
        api_test.sanity = True if c[s]['sanity'] == "True" else False
        api_test.api_endpoint = c[s]['api_endpoint']
        api_test.api_method = c[s]['api_method']
        api_test.api_message_body = c[s]['api_message_body']
        api_test.expected_status_code = c[s]['expected_status_code']
        api_test.expected_response_body = c[s]['expected_response_body']
        api_test.evaluation = eval_id
        api_test.save()


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
        message_sanity += "<br> Sanity Test Failed. Hence further tests not evaluated."
        submission.marks = 0
        submission.message = message_sanity
        submission.save()
        return
    marks, message = run_tests(normal_tests, public_ip)
    submission.marks = marks
    submission.message = message
    submission.save()
    return


def run_tests(test_objects, public_ip):
    marks = 0
    message = ""
    for test in test_objects:
        if test.api_method == "GET":
            response = requests.get(public_ip+test.api_endpoint)
            if response.status_code == test.expected_status_code:
                marks += 1
                message += "<br> " + test.api_endpoint + " passed"
            else:
                message += "<br> " + test.api_endpoint + "failed"
        elif test.api_method == "POST":
            requests.post("todo")
        elif test.api_method == "PUT":
            requests.put("todo")
    return marks, message


