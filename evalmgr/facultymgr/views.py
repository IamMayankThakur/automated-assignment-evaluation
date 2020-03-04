"""
API conf format
[Settings]
name = Assignment 1 Eval Cloud Computing
description = CC A 1
email = instructor1@mail.com
access_code = UE17CS302
test_type = 1
[TestName]
sanity = True
api_endpoint = api/v1/test
api_method = GET
api_message_body = {key: value}
expected_status_code = 201
expected_response_body = {key:value}
"""

# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Evaluation
from .utils import create_evaluation, create_evaluation_code_eval
from testmgr.models import CodeEvalModel


class ConfigUpload(View):
    def get(self, request):
        return render(request, 'choose_file.html')

    def post(self, request):
        try:
            eval_conf = request.FILES['conf_file']
            evaluation = Evaluation()
            evaluation.conf_file = eval_conf
            evaluation.save()
            create_evaluation(eval_id=evaluation.id)
            return HttpResponse("Config created")
        except Exception as e:
            print(e)
            return HttpResponse("Error")

class ConfigUpload2(View):
    def get(self, request):
        return render(request, 'code_eval_faculty_file.html')

    def post(self, request):
        try:
            eval_conf = request.FILES['conf_file']
            evaluation = Evaluation()
            evaluation.conf_file = eval_conf
            evaluation.save()
            create_evaluation_code_eval(eval_id=evaluation.id)
            eval_dock = request.FILES['docker_file']
            eval_main = request.FILES['main_file']
            code_eval_model = CodeEvalModel()
            code_eval_model.dock_file = eval_dock
            code_eval_model.main_file = eval_main
            code_eval_model.evaluation = Evaluation.objects.get(id=evaluation.id)
            code_eval_model.save()
            return HttpResponse("Config created and docker and main in table")
        except Exception as e:
            print(e)
            return HttpResponse("Error")
