import configparser
import requests

from .models import ApiTestModel
from ..facultymgr.models import Evaluation


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
        api_test.api_endpoint = c[s]['api_endpoint']
        api_test.api_method = c[s]['api_method']
        api_test.api_message_body = c[s]['api_message_body']
        api_test.expected_status_code = c[s]['expected_status_code']
        api_test.expected_response_body = c[s]['expected_response_body']
        api_test.evaluation = eval_id
        api_test.save()


def do_api_eval(*args, **kwargs):
    pass
