import configparser
from .models import Evaluation, FacultyProfile
from testmgr.api_eval import setup_api_eval
from studentmgr.models import Team
import pandas as pd
from testmgr.code_eval import setup_code_eval
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


def create_evaluation(**kwargs):
    eval_id = kwargs["eval_id"] if "eval_id" in kwargs else None
    if eval_id is None:
        raise RuntimeError
    try:
        evaluation = Evaluation.objects.get(pk=eval_id)
        file = evaluation.conf_file.path
        c = configparser.ConfigParser()
        c.read(file)
        faculty = FacultyProfile.objects.get(email=c["Settings"]["email"])
        evaluation.name = c["Settings"]["name"]
        evaluation.description = c["Settings"]["description"]
        evaluation.created_by = faculty
        evaluation.type = c["Settings"]["test_type"]
        evaluation.access_code = c["Settings"]["access_code"]
        evaluation.save()
        setup_api_eval.delay(eval_id=eval_id)
        # setup_api_eval(eval_id=eval_id)
    except Exception as e:
        print(e)


def port_csv_to_db(csv_path):
    df = pd.read_csv(csv_path)
    for index, row in df.iterrows():
        try:
            team_obj = Team(
                team_name=row["Team Name"],
                email_member_1=row["Email(Member 1)"],
                email_member_2=row["Email(Member 2)"],
                email_member_3=row["Email(Member 3)"],
                email_member_4=row["Email (Member 4)"],
            )
            team_obj.save()
        except Exception as e:
            print(e)
            print("Invalid row")


def create_evaluation_code_eval(**kwargs):
    eval_id = kwargs["eval_id"] if "eval_id" in kwargs else None
    if eval_id is None:
        raise RuntimeError
    try:
        evaluation = Evaluation.objects.get(pk=eval_id)
        file = evaluation.conf_file.path
        c = configparser.ConfigParser()
        c.read(file)
    except ObjectDoesNotExist:
        return HttpResponse("Evaluation object not created")
    try:
        faculty = FacultyProfile.objects.get(email=c["Settings"]["email"])
        evaluation.name = c["Settings"]["name"]
        evaluation.description = c["Settings"]["description"]
        evaluation.created_by = faculty
        evaluation.type = c["Settings"]["test_type"]
        evaluation.access_code = c["Settings"]["access_code"]
        evaluation.save()
        setup_code_eval.delay(eval_id=eval_id)
    except ObjectDoesNotExist:
        return HttpResponse("FacultyProfile object not found")


def create_evaluation_container_eval(**kwargs):
    eval_id = kwargs["eval_id"] if "eval_id" in kwargs else None
    if eval_id is None:
        raise RuntimeError
    try:
        evaluation = Evaluation.objects.get(pk=eval_id)
    except ObjectDoesNotExist:
        return HttpResponse("Evaluation object not created")
    try:
        evaluation.created_by = FacultyProfile.objects.get(
            email=kwargs["form_data"]["email_id"]
        )
        evaluation.name = kwargs["form_data"]["evaluation_name"]
        evaluation.type = kwargs["form_data"]["testType"]
        evaluation.access_code = kwargs["form_data"]["access_code"]
        evaluation.description = kwargs["form_data"]["description"]
        evaluation.save()
        endpoint = get_route_for_eval((int)(kwargs["form_data"]["testType"]))
        return HttpResponseRedirect(reverse(endpoint))
    except (ObjectDoesNotExist, IntegrityError):
        evaluation.delete()
        return HttpResponse(
            "FacultyProfile object not found (or) Please enter unique/correct values, the access code or name could have been taken by another evaluation"
        )


def get_route_for_eval(testType):
    if testType == 4:
        return "facultymgr:container_test_cases"
    if testType == 5:
        return "facultymgr:scale_test_cases"
