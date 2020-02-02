from django.contrib import admin

# Register your models here.

from studentmgr.models import Team, Submission
from .models import FacultyProfile, Evaluation
from testmgr.models import ApiTestModel

admin.site.register(Team)
admin.site.register(Submission)
admin.site.register(FacultyProfile)
admin.site.register(Evaluation)
admin.site.register(ApiTestModel)