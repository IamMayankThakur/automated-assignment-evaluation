import configparser
from .models import Evaluation, FacultyProfile
from testmgr.api_eval import setup_api_eval
from studentmgr.models import Team
import pandas as pd

def create_evaluation(**kwargs):
    eval_id = kwargs['eval_id'] if 'eval_id' in kwargs else None
    if eval_id is None:
        raise RuntimeError
    try:
        evaluation = Evaluation.objects.get(pk=eval_id)
        file = evaluation.conf_file.path
        c = configparser.ConfigParser()
        c.read(file)
        faculty = FacultyProfile.objects.get(email=c['Settings']['email'])
        evaluation.name = c['Settings']['name']
        evaluation.description = c['Settings']['description']
        evaluation.created_by = faculty
        evaluation.type = c['Settings']['test_type']
        evaluation.access_code = c['Settings']['access_code']
        evaluation.save()
        setup_api_eval(eval_id=eval_id)
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
                email_member_4=row["Email(Member 4)"]
            )
            team_obj.save()
        except Exception as e:
            print(e)
            print("Invalid row")
