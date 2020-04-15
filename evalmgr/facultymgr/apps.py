from django.apps import AppConfig


class FacultymgrConfig(AppConfig):
    name = "facultymgr"

    def ready(self):
        try:
            from django.contrib.auth.models import Group

            Group.objects.get_or_create(name="student")
            Group.objects.get_or_create(name="faculty")
        except Exception as e:
            print("No auth_group, run migrations and then student/faculty groups can be created.")
