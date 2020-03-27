from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views import View

from facultymgr.models import Evaluation
from testmgr.api_eval import do_api_eval, do_api_eval_cc
from testmgr.container_eval import do_container_eval_cc
from testmgr.code_eval import do_code_eval
from .models import Team, Submission
from .utils import get_route_for_eval_type


class AccessCodeView(View):
    def get(self, request):
        return render(request, "accesskey_file.html")

    def post(self, request):
        try:
            code = request.POST["access_code"]
            request.session["access_code"] = code
            evaluation = Evaluation.objects.get(access_code=code)
            endpoint = get_route_for_eval_type(evaluation.type)
            return HttpResponseRedirect(reverse(endpoint))
        except Exception as e:
            print(e)
            return HttpResponse("Error in access code")


class ApiTestView(View):
    def get(self, request):
        if request.session.get("access_code") is None:
            return HttpResponse("No access code")
        return render(request, "testapi_file.html")

    def post(self, request):
        try:
            sub = Submission()
            sub.team = Team.objects.get(team_name=request.POST["team"])
            sub.evaluation = Evaluation.objects.get(
                access_code=request.session["access_code"]
            )
            sub.public_ip_address = "http://" + request.POST["public_ip_address"]
            sub.source_code_file = request.FILES["source_code_file"]
            sub.above_specification_choice = request.POST["above_specification_choice"]
            sub.above_specification = "".join(
                request.POST.getlist("above_specification")
            )
            sub.above_specification_file = request.FILES["above_specification_file"]
            sub.save()
            # do_api_eval.delay(sub_id=sub.id)
            do_api_eval_cc.delay(sub_id=sub.id)
            # do_api_eval(sub_id=sub.id)
            return HttpResponse(
                "Your submission has been recorded. Your submission id is "
                + str(sub.id)
            )
        except Exception as e:
            print(e)
            return HttpResponse("Error in input, ensure all fields are filled")


class PastSubmissionView(View):
    def post(self, request):
        team_name = request.POST['team_name']
        data = Submission.objects.filter(team__team_name=team_name)
        submissions = {'submissions': data}
        # return render(request, 'submissions.html', submissions)
        return HttpResponse("Marks will not be shown at this point")


class ContainerTestView(View):
    def get(self, request):
        if request.session.get("access_code") is None:
            return HttpResponse("No access code")
        return render(request, "cc_a2.html")

    def post(self, request):
        try:
            # return HttpResponse("Submission Closed.!")
            sub = Submission()
            sub.team = Team.objects.get(team_name=request.POST["team"])
            sub.evaluation = Evaluation.objects.get(
                access_code=request.session["access_code"]
            )
            sub.username = request.POST["username"]
            sub.private_key_file = request.FILES["private_key_file"]
            sub.source_code_file = request.FILES["source_code_file"]
            sub.public_ip_address = request.POST["public_ip_address"]
            sub.save()
            print(sub.username, sub.public_ip_address, sub.id)
            do_container_eval_cc.delay(sub_id=sub.id)
            return HttpResponse("Submission Recorded with submission id " + str(sub.id))
        except Exception as e:
            print(e)
            return HttpResponse("Submission failed. Enter valid data")


class CodeEvalTestView(View):
    def get(self, request):
        if request.session.get("access_code") is None:
            return HttpResponse("No access code")
        return render(request, "code_eval_submission.html")

    def post(self, request):
        try:
            sub = Submission()
            sub.team = Team.objects.get(team_name=request.POST["team"])
            sub.evaluation = Evaluation.objects.get(
                access_code=request.session["access_code"]
            )
            sub.source_code_file = request.FILES["source_code_file"]
            sub.save()
            do_code_eval.delay(sub_id=sub.id)
            return HttpResponse(
                "Your submission has been recorded. Your submission id is "
                + str(sub.id)
            )
        except Exception as e:
            print(e)
            return HttpResponse("Error in input, ensure all fields are filled")
