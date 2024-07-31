from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Vulnerability, Mission
from django.shortcuts import render, redirect
from .forms import VulnerabilityForm, MissionStatusForm
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        
        context['segment'] = load_template

        # Check if the path contains 'mission' and handle accordingly
        if load_template == 'report_vulnerability':
            return redirect('mission/report.html')

        # Render the generic template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        print(f"Template {load_template} does not exist.")
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(f"An error occurred: {e}")
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

#-------------------------------------------------------------------------------------------------

    
# Listing vulnerabilities
@login_required
def vulnerability_list(request):
    vulnerabilities = Vulnerability.objects.all()
    return render(request, 'mission/vulnerabilityList.html', {'vulnerabilities': vulnerabilities})
#-------------------------------------------------------------------------------------------------


# Report vulnerability
@login_required
def report_vulnerability(request):
    if request.method == 'POST':
        form = VulnerabilityForm(request.POST)
        if form.is_valid():
            vulnerability = form.save(commit=False)
            vulnerability.reported_by = request.user
            vulnerability.save()
            # Create mission after vulnerability is reported
            Mission.objects.create(
                state='Reported',
                asset=vulnerability.asset,
                vulnerability=vulnerability,
                priority=vulnerability.vuln_severity,
                due_date=datetime.date.today() 
            )
            messages.success(request, 'Vulnerability reported successfully.')
            return redirect('report_vulnerability')
    else:
        form = VulnerabilityForm()
    return render(request, 'mission/report.html', {'form': form})

#-------------------------------------------------------------------------------------------------


# Mission Interface
@login_required
def mission_list(request):
    missions = Mission.objects.all()
    return render(request, 'mission/mission_list.html', {'missions': missions})

@login_required
def mission_detail(request, id):
    mission = get_object_or_404(Mission, mission_id=id)
    return render(request, 'mission/mission_detail.html', {'mission': mission})

@login_required
def update_mission_status(request, id):
    mission = get_object_or_404(Mission, mission_id=id)
    if request.method == 'POST':
        form = MissionStatusForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            return redirect('mission_list')
    else:
        form = MissionStatusForm(instance=mission)
    return render(request, 'mission/update_status.html', {'form': form, 'mission': mission})
#-------------------------------------------------------------------------------------------------