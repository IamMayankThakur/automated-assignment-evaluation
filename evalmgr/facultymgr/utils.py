import configparser
import csv

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.http import HttpResponse

from studentmgr.models import Team, Submission
from testmgr.api_eval import setup_api_eval
from testmgr.code_eval import setup_code_eval
from .models import Evaluation, FacultyProfile


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


def get_max_marks():
    a1 = list(
        Submission.objects.filter(evaluation=2)
        .values("team__team_name")
        .annotate(Max("marks"))
    )
    a2 = list(
        Submission.objects.filter(evaluation=4)
        .values("team__team_name")
        .annotate(Max("marks"))
    )
    a3 = list(
        Submission.objects.filter(evaluation=5)
        .values("team__team_name")
        .annotate(Max("marks"))
    )
    all_rows = []
    team_usn_mapping = {}
    csv_file = csv.reader(open("../../teamslist.csv", "r"), delimiter=",")
    for row in csv_file:
        print(row)
        team_usn_mapping[row[24]] = []
    csv_file = csv.reader(open("new_bd_resp.csv", "r"), delimiter=",")
    for row in csv_file:
        team_usn_mapping[row[24]].append([row[1], row[2], row[3]])
        team_usn_mapping[row[24]].append([row[5], row[6], row[7]])
        if row[10] != "":
            team_usn_mapping[row[24]].append([row[10], row[11], row[12]])
        if row[15] != "":
            team_usn_mapping[row[24]].append([row[15], row[16], row[17]])

    for i in range(len(s1)):
        try:
            usn_list = team_usn_mapping[s1[i]["team__team_name"]]
            print("team exists")
        except Exception as e:
            print("team does not exist")
            continue
        for usn in usn_list:
            print(usn)
            all_rows.append(
                [
                    usn[0],
                    usn[2],
                    usn[1],
                    s1[i]["score_1__max"],
                    #  s2[i]['score_2__max'], s3[i]['score_3__max'],
                    s2[i]["score_2__max"],
                    s1[i]["team__team_name"],
                ]
            )
    with open("marks_a3.csv", "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(all_rows)
    csvFile.close()
