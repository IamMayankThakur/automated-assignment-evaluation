from django.contrib import admin
from django.contrib.auth.models import Group, User

# Register your models here.

from studentmgr.models import (
    Team,
    Submission,
    SubmissionAssignment3,
)
from .models import Evaluation
from testmgr.models import ApiTestModel, CodeEvalTestModel, CodeEvalModel


# admin.site.unregister(User)
# admin.site.unregister(Group)

admin.site.site_header = "Evaluation Dashboard"


class CustomSubmission(admin.ModelAdmin):
    list_display = ("id", "team", "timestamp", "marks")
    list_filter = ("team", "timestamp", "marks")


admin.site.register(Team)
admin.site.register(Submission, CustomSubmission)
admin.site.register(Evaluation)
admin.site.register(ApiTestModel)
admin.site.register(CodeEvalTestModel)
admin.site.register(CodeEvalModel)
admin.site.register(SubmissionAssignment3, CustomSubmission)
