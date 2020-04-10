from django.apps import AppConfig


class FacultymgrConfig(AppConfig):
    name = "facultymgr"

    def ready(self):
        from django.contrib.auth.models import Group

        Group.objects.get_or_create(name="student")
        Group.objects.get_or_create(name="faculty")
