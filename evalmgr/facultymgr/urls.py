from django.urls import path
from . import views

app_name = "facultymgr"

urlpatterns = [
    path("upload_config", views.ConfigUpload.as_view(), name="create_api_eval"),
    path(
        "upload_config2", views.ConfigUploadCodeEval.as_view(), name="create_code_eval"
    ),
    path("create_eval", views.CreateEval.as_view(), name="create_eval"),
    path(
        "container_test_cases",
        views.ContainerTestCases.as_view(),
        name="container_test_cases",
    ),
    path("scale_test_cases", views.ScaleTestCases.as_view(), name="scale_test_cases"),
    path("view_submissions", views.SubmissionView.as_view(), name="view_submission"),
]
