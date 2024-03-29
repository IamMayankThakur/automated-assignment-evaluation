from django.urls import path
from . import views

app_name = "studentmgr"

urlpatterns = [
    path("join/", views.AccessCodeView.as_view(), name="access_code"),
    path("api_test/", views.ApiTestView.as_view(), name="api_view"),
    path("container_test/", views.ContainerTestView.as_view(), name="container_view"),
    path(
        "submissions/", views.PastSubmissionView.as_view(), name="past_submission_view"
    ),
    path("code_eval_test/", views.CodeEvalTestView.as_view(), name="code_eval_view"),
    path(
        "load_balancer_test/", views.LoadBalancerTestView.as_view(), name="lb_eval_view"
    ),
    path(
        "container_eval_test/",
        views.ContainerEvalTestView.as_view(),
        name="container_eval_view",
    ),
    path("scale_eval_test/", views.ScaleTestView.as_view(), name="scale_eval_view"),
    path(
        "final_project_test/",
        views.FinalProjectTestView.as_view(),
        name="final_project_view",
    ),
]
