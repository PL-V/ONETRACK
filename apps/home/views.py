from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Vulnerability, Mission
from django.shortcuts import render, redirect
from .forms import VulnerabilityForm, MissionStatusForm, MissionAssignForm
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages




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

# Assigning missions
@login_required(login_url="/login/")
def assign_mission(request, id):
    mission = get_object_or_404(Mission, mission_id=id)
    if request.user.role != 'Owner':
        messages.error(request, 'You do not have permission to assign missions.')
        return redirect('mission_detail', id=id)

    if request.method == 'POST':
        form = MissionAssignForm(request.POST, instance=mission)
        if form.is_valid():
            assigned_user = form.cleaned_data['assigned_to']
            mission = form.save(commit=False)
            mission.state = 'Assigned'
            mission.save()
            # Update the associated vulnerability's assigned_to attribute
            mission.vulnerability.assigned_to = assigned_user
            mission.vulnerability.save()
            
            messages.success(request, 'Mission assigned successfully.')
            return redirect('assign_mission', id=id)
    else:
        form = MissionAssignForm(instance=mission)
    
    return render(request, 'mission/assign_mission.html', {'form': form, 'mission': mission})
#-------------------------------------------------------------------------------------------------
