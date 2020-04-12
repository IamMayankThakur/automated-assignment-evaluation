from django.urls import path
from . import views

app_name = "facultymgr"

urlpatterns = [
    path("upload_config", views.ConfigUpload.as_view()),
    path("upload_config2", views.ConfigUploadCodeEval.as_view()),
    path("view_submissions", views.SubmissionView.as_view(), name="view_submission"),
]
