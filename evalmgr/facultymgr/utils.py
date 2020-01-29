import configparser
from .models import Evaluation, FacultyProfile


def create_evaluation(**kwargs):
    submission_id = kwargs['sub_id'] if 'sub_id' in kwargs else None
    if submission_id is None:
        raise ImportError
    try:
        evaluation = Evaluation.objects.get(pk=submission_id)
        file = evaluation.path
        c = configparser.ConfigParser()
        c.read(file)
        faculty = FacultyProfile.objects.get(email=c['Settings']['email'])
        evaluation.name = c['Settings']['name']
        evaluation.description = c['Settings']['description']
        evaluation.created_by = faculty
        evaluation.type = c['Settings']['test_type']
        evaluation.code = c['Settings']['code']
        evaluation.save()
    except Exception as e:
        print(e)
