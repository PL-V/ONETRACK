from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Vulnerability, Mission, MissionHistory
from django.shortcuts import render, redirect
from .forms import VulnerabilityForm, MissionStatusForm, MissionAssignForm,  MissionForm
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone


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
    user_roles = request.user.roles.values_list('name', flat=True)
    
    if request.user.is_superuser:
        missions = Mission.objects.all()
    else:
        missions = Mission.objects.filter(vulnerability__assigned_to=request.user)
    
    context = {
        'missions': missions,
        'user_roles': user_roles,
    }
    
    return render(request, 'mission/mission_list.html', context)

@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    user_roles = request.user.roles.values_list('name', flat=True)
    context = {
        'mission': mission,
        'user_roles': user_roles,
    }
    return render(request, 'mission/mission_detail.html', context)

@login_required
def start_remediation(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'In Remediation'
    mission.save()
    messages.success(request, 'Mission status updated to "In Remediation".')
    return redirect('mission_detail', mission_id=mission_id)


#-------------------------------------------------------------------------------------------------


# Assigning missions
@login_required(login_url="/login/")
def assign_mission(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    # if not (request.user.roles.filter(name='Owner').exists() or 
    #         request.user.roles.filter(name='Superuser').exists()):
    #     messages.error(request, 'You do not have permission to assign missions.')
    #     return redirect('mission_detail', mission_id=mission_id)

    if request.method == 'POST':
        form = MissionAssignForm(request.POST, instance=mission)
        if form.is_valid():
            assigned_user = form.cleaned_data['assigned_to']
            mission = form.save(commit=False)
            mission.status = 'Assigned'
            mission.save()
            # Update the associated vulnerability's assigned_to attribute
            mission.vulnerability.assigned_to = assigned_user
            mission.vulnerability.save()
            
            messages.success(request, 'Mission assigned successfully.')
            return redirect('assign_mission', mission_id=mission_id)
    else:
        form = MissionAssignForm(instance=mission)
    
    return render(request, 'mission/assign_mission.html', {'form': form, 'mission': mission})
#-------------------------------------------------------------------------------------------------




# New mission section:
@login_required
def create_mission(request):
    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            vuln_name = form.cleaned_data['vuln_name']
            vuln_type = form.cleaned_data['vuln_type']
            vuln_severity = form.cleaned_data['vuln_severity']
            vuln_description = form.cleaned_data['vuln_description']
            cve = form.cleaned_data['cve']
            risk = form.cleaned_data['risk']
            source = form.cleaned_data['source']
            assets = form.cleaned_data['assets']

            # Create a single vulnerability entry with multiple assets
            vulnerability = Vulnerability.objects.create(
                vuln_name=vuln_name,
                vuln_type=vuln_type,
                vuln_severity=vuln_severity,
                vuln_description=vuln_description,
                cve=cve,
                risk=risk,
                source=source,
                reported_by=request.user
            )
            vulnerability.asset.set(assets)  # Assuming assets is a ManyToManyField in the Vulnerability model

            # Create a mission for the vulnerability
            mission = Mission.objects.create(
                status='Reported',
                priority=vuln_severity,
                due_date=timezone.now().date(),
                vulnerability=vulnerability
            )
            mission.asset.set(assets)  # Assuming assets is a ManyToManyField in the Mission model

            # Create initial mission history
            MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                state_on_change_date='Mission created with status Reported'
            )

            messages.success(request, 'Mission created successfully.')
            return redirect('create_mission')  # Adjust the redirect as needed
    else:
        form = MissionForm()

    return render(request, 'mission/create_mission.html', {'form': form})
#-------------------------------------------------------------------------------------------------

