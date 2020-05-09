import configparser
import csv
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Max

from studentmgr.models import Team, Submission, SubmissionAssignment3
from testmgr.api_eval import setup_api_eval
from testmgr.code_eval import setup_code_eval
from .models import Evaluation


def create_evaluation(**kwargs):
    eval_id = kwargs["eval_id"] if "eval_id" in kwargs else None
    if eval_id is None:
        raise RuntimeError
    try:
        evaluation = Evaluation.objects.get(pk=eval_id)
        file = evaluation.conf_file.path
        c = configparser.ConfigParser()
        c.read(file)
        faculty = User.objects.get(email=c["Settings"]["email"])
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
        faculty = User.objects.get(email=c["Settings"]["email"])
        evaluation.name = c["Settings"]["name"]
        evaluation.description = c["Settings"]["description"]
        evaluation.created_by = faculty
        evaluation.type = c["Settings"]["test_type"]
        evaluation.access_code = c["Settings"]["access_code"]
        evaluation.save()
        setup_code_eval.delay(eval_id=eval_id)
    except ObjectDoesNotExist:
        return HttpResponse("FacultyProfile object not found")


def filter_on_team_name(l, team_name):
    for i in l:
        if i[0] == team_name:
            return i[1]
    return "MARKS_NOT_FOUND"


def get_max_marks():
    a1 = list(
        Submission.objects.filter(evaluation=3)
        .values_list("team__team_name")
        .annotate(Max("marks"))
    )
    a2 = list(
        Submission.objects.filter(evaluation=4)
        .values_list("team__team_name")
        .annotate(Max("marks"))
    )
    a3 = list(
        SubmissionAssignment3.objects.filter(evaluation=5)
        .values_list("team__team_name")
        .annotate(Max("marks"))
    )
    all_rows = []

    columns = [
        "USN",
        "Name",
        "Email ID",
        "Team Name",
        "Assignment 1 Marks",
        "Assignment 2 Marks",
        "Assignment 3 Marks",
    ]
    df = pd.read_csv("teamslist.csv")
    for index, row in df.iterrows():
        new_row = []
        if row["SRN (Member 1)"] != "nan":
            new_row.append(row["SRN (Member 1)"])
            new_row.append(row["Name (Member 1)"])
            new_row.append(row["Email(Member 1)"])
            new_row.append(row["Team Name"])
            new_row.append(filter_on_team_name(a1, row["Team Name"]))
            new_row.append(filter_on_team_name(a2, row["Team Name"]))
            new_row.append(filter_on_team_name(a3, row["Team Name"]))
            all_rows.append(new_row)
        new_row = []
        if row["SRN (Member 2)"] != "nan":
            new_row.append(row["SRN (Member 2)"])
            new_row.append(row["Name (Member 2)"])
            new_row.append(row["Email(Member 2)"])
            new_row.append(row["Team Name"])
            new_row.append(filter_on_team_name(a1, row["Team Name"]))
            new_row.append(filter_on_team_name(a2, row["Team Name"]))
            new_row.append(filter_on_team_name(a3, row["Team Name"]))
            all_rows.append(new_row)
        new_row = []
        if row["SRN (Member 3)"] != "nan":
            new_row.append(row["SRN (Member 3)"])
            new_row.append(row["Name(Member 3)"])
            new_row.append(row["Email(Member 3)"])
            new_row.append(row["Team Name"])
            new_row.append(filter_on_team_name(a1, row["Team Name"]))
            new_row.append(filter_on_team_name(a2, row["Team Name"]))
            new_row.append(filter_on_team_name(a3, row["Team Name"]))
            all_rows.append(new_row)
        new_row = []
        if row["SRN (Member 4)"] != "nan":
            new_row.append(row["SRN (Member 4)"])
            new_row.append(row["Name (Member 4)"])
            new_row.append(row["Email (Member 4)"])
            new_row.append(row["Team Name"])
            new_row.append(filter_on_team_name(a1, row["Team Name"]))
            new_row.append(filter_on_team_name(a2, row["Team Name"]))
            new_row.append(filter_on_team_name(a3, row["Team Name"]))
            all_rows.append(new_row)
    final_data = pd.DataFrame(all_rows, columns=columns)
    final_data.to_csv("final_marks.csv")


def create_evaluation_container_eval(**kwargs):
    eval_id = kwargs["eval_id"] if "eval_id" in kwargs else None
    if eval_id is None:
        raise RuntimeError
    try:
        evaluation = Evaluation.objects.get(pk=eval_id)
    except ObjectDoesNotExist:
        return HttpResponse("Evaluation object not created")
    try:
        evaluation.created_by = User.objects.get(email=kwargs["form_data"]["email_id"])
        evaluation.name = kwargs["form_data"]["evaluation_name"]
        evaluation.type = kwargs["form_data"]["testType"]
        evaluation.access_code = kwargs["form_data"]["access_code"]
        evaluation.description = kwargs["form_data"]["description"]
        evaluation.save()
        endpoint = get_route_for_eval(int(kwargs["form_data"]["testType"]))
        return HttpResponseRedirect(reverse(endpoint))
    except (ObjectDoesNotExist, IntegrityError):
        evaluation.delete()
        return HttpResponse(
            "FacultyProfile object not found (or) Please enter unique/correct values, the access code or name could have been taken by another evaluation"
        )


def get_route_for_eval(testType):
    if testType == 5:
        return "facultymgr:container_test_cases"
    if testType == 6:
        return "facultymgr:scale_test_cases"


class SignUpForm(UserCreationForm):
    username = forms.CharField()
    first_name = forms.CharField(max_length=32, help_text="First name")
    last_name = forms.CharField(max_length=32, help_text="Last name")
    email = forms.EmailField(max_length=64, help_text="Enter a valid email address")
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("first_name", "last_name", "email",)
