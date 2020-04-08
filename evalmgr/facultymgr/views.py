# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.db import InternalError, DatabaseError
from django.db.utils import IntegrityError
from .models import Evaluation
from testmgr.models import ContainerTestModel
from .utils import (
    create_evaluation,
    create_evaluation_code_eval,
    create_evaluation_container_eval,
)
from testmgr.models import CodeEvalModel
from testmgr.container_eval_final import setup_container_eval
from testmgr.scale_eval import setup_scale_eval
from django.http import HttpResponseRedirect
from django.urls import reverse
import docker

path = "/home/nihali/work/8thsem/code/automated-assignment-evaluation/evalmgr/media/conf/dockerfile/"


class ConfigUpload(View):
    def get(self, request):
        return render(request, "choose_file.html")

    def post(self, request):
        try:
            eval_conf = request.FILES["conf_file"]
            evaluation = Evaluation()
            evaluation.conf_file = eval_conf
            evaluation.save()
            create_evaluation(eval_id=evaluation.id)
            return HttpResponse("Config created")
        except Exception as e:
            print(e)
            return HttpResponse("Error")


class ConfigUploadCodeEval(View):
    def get(self, request):
        return render(request, "code_eval_faculty_file.html")

    def post(self, request):
        # try:
        eval_conf = request.FILES["conf_file"]
        evaluation = Evaluation()
        evaluation.conf_file = eval_conf
        evaluation.save()
        # except Exception:
        # return HttpResponse("Error Evaluation Object could not be created")
        create_evaluation_code_eval(eval_id=evaluation.id)
        try:
            eval_dock = request.FILES["docker_file"]
            eval_main = request.FILES["main_file"]
            eval_output_expected = request.FILES["expected_output_file"]
            eval_command = request.POST.get("command")
            code_eval_model = CodeEvalModel()
            code_eval_model.docker_file = eval_dock
            code_eval_model.main_file = eval_main
            code_eval_model.expected_output_file = eval_output_expected
            code_eval_model.command = eval_command
            code_eval_model.evaluation = Evaluation.objects.get(id=evaluation.id)
            code_eval_model.save()

            path = code_eval_model.docker_file.path
            print(path)
            path = path.rsplit("/", 1)[0]
            print(code_eval_model.docker_file)
            client = docker.from_env()
            client.images.build(
                path=path, tag={"image5"},
            )
            # print("IMAGES", client.images.list(tag="image1"))

            return HttpResponse("Config created and docker and main in table")
        except ObjectDoesNotExist:
            return HttpResponse("Error in creating object in CodeEvalModel")


class CreateEval(View):
    def get(self, request):
        return render(request, "create_eval.html")

    def post(self, request):
        try:
            evaluation = Evaluation()
            evaluation.save()
        except InternalError:
            return HttpResponse("Error Evaluation object could not be created")
        request.session["eval_id"] = evaluation.id
        return create_evaluation_container_eval(
            eval_id=evaluation.id, form_data=request.POST
        )


class ContainerTestCases(View):
    def get(self, request):
        print(request.session["eval_id"])
        testcases = {"eval_id": request.session["eval_id"]}
        return render(request, "container_test_cases.html", testcases)

    def post(self, request):
        try:
            if "finish" in request.POST:
                return render(request, "eval_created.html")
            setup_container_eval.delay(form_data=request.POST)
            if "another" in request.POST:
                testcases = {"eval_id": request.POST["eval_id"]}
                return render(request, "container_test_cases.html", testcases)
        except ObjectDoesNotExist:
            return HttpResponse("Evaluation object not found")


class ScaleTestCases(View):
    def get(self, request):
        print(request.session["eval_id"])
        eval_id = {"eval_id": request.session["eval_id"]}
        return render(request, "scale_test_cases.html", eval_id)

    def post(self, request):
        try:
            if "finish" in request.POST:
                return render(request, "eval_created.html")
            setup_scale_eval(form_data=request.POST)
            if "another" in request.POST:
                eval_id = {"eval_id": request.POST["eval_id"]}
                return render(request, "scale_test_cases.html", eval_id)
        except ObjectDoesNotExist:
            return HttpResponse("Evaluation object not found")
