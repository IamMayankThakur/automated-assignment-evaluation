from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.views import View
from facultymgr.models import Evaluation
from .models import Team, Submission
from.utils import get_route_for_eval_type
# Create your views here.


class AccessCodeView(View):
    def get(self, request):
        return render(request, 'accesskey_file.html')

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
        return render(request, 'testapi_file.html')

    def post(self, request):
        # try:
            sub = Submission()
            import pdb
            pdb.set_trace()
            sub.team = Team.objects.get(team_name=request.POST['team'])
            sub.evaluation = Evaluation.objects.get(access_code=request.session['access_code'])
            sub.public_ip_address = request.POST['public_ip_address']
            sub.source_code_file = request.FILES['source_code_file']
            sub.above_specification_choice = request.POST['above_specification_choice']
            sub.above_specification = ''.join(request.POST.getlist('above_specification'))
            sub.above_specification_file = request.FILES['above_specification_file']
            sub.save()
            return HttpResponse("Your submission has been recorded. Your submission id is "+str(sub.id))
        # except Exception as e:
        #     print(e)
        #     return HttpResponse("Error while API submission")


class PastSubmissionView(View):
    def post(self, request):
        team_name = request.POST['team_name']
        data = Submission.objects.filter(team__team_name=team_name)
        # submissions = [{'id': s.pk, 'marks': s.marks, 'timestamp': s.timestamp, 'message':s.message} for s in data]
        submissions = {'submissions': data}
        return render(request, 'submissions.html', submissions)
