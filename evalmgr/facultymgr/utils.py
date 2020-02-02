import configparser
from .models import Evaluation, FacultyProfile
from testmgr.api_eval import setup_api_eval


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
