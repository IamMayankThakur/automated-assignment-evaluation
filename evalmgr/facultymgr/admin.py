from django.contrib import admin
from django.contrib.auth.models import Group, User
# Register your models here.

from studentmgr.models import Team, Submission
from .models import FacultyProfile, Evaluation
from testmgr.models import ApiTestModel


# admin.site.unregister(User)
# admin.site.unregister(Group)

admin.site.site_header = 'Evaluation Dashboard'

class CustomSubmission(admin.ModelAdmin):
    list_display = ('id', 'team', 'timestamp', 'marks')
    list_filter = ('team', 'timestamp', 'marks')

admin.site.register(Team)
admin.site.register(Submission, CustomSubmission)
admin.site.register(FacultyProfile)
admin.site.register(Evaluation)
admin.site.register(ApiTestModel)