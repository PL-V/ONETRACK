from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Vulnerability, Mission, MissionHistory, Asset
from django.shortcuts import render, redirect
from .forms import VulnerabilityForm, MissionAssignForm,  MissionForm, AssetOwnerAssignForm
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .utils import send_email


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


# Mission List Section
@login_required
def mission_list(request):
    user_roles = request.user.roles.values_list('name', flat=True)
    
    if request.user.is_superuser or 'Verifier' in user_roles:
        missions = Mission.objects.all()
    elif 'Owner' in user_roles:
        missions = Mission.objects.filter(asset__owner=request.user).distinct()
    else:
        missions = Mission.objects.filter(vulnerability__assigned_to=request.user).distinct()
    
    context = {
        'missions': missions,
        'user_roles': user_roles,
    }
    
    return render(request, 'mission/mission_list.html', context)

@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    user_roles = request.user.roles.values_list('name', flat=True)

    # Check if the user is the owner of any of the affected assets
    is_owner_of_affected_assets = mission.asset.filter(owner=request.user).exists()
    context = {
        'mission': mission,
        'user_roles': user_roles,
        'is_owner_of_affected_assets': is_owner_of_affected_assets,
    }
    return render(request, 'mission/mission_detail.html', context)
#-------------------------------------------------------------------------------------------------

# Remediation section
@login_required
def start_remediation(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'In Remediation'
    mission.save()
    messages.success(request, 'Mission status updated to "In Remediation".')
    return redirect('mission_detail', mission_id=mission_id)

@login_required
def ending_remediation(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'Remediated'
    mission.save()
    messages.success(request, 'Mission status updated to "Remediated".')
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

            # # Send email to the asset owner
            # subject = f"You are assigned to remediate the mission with id: {mission.mission_id}"
            # template_name = 'emails/assign_mission.html'
            # context = {'mission': mission, 'assigned_user': assigned_user}
            # recipient_list = [assigned_user.email]
            # send_email(subject, template_name, context, recipient_list)
            
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
            vulnerability.asset.set(assets)  # assets is a ManyToManyField in the Vulnerability model

            # Create a mission for the vulnerability
            mission = Mission.objects.create(
                status='Reported',
                priority=vuln_severity,
                due_date=timezone.now().date(),
                vulnerability=vulnerability
            )
            mission.asset.set(assets)  

            # Create initial mission history
            MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                state_on_change_date='Mission created with status Reported'
            )
            
            # # Send email to the asset owner
            # asset_owners = {asset.owner for asset in assets if asset.owner}
            # # Create a set to track unique owners
            # unique_owners = set(asset_owners)
            # for owner in unique_owners:
            #     subject = "New Mission Reported"
            #     template_name = 'emails/new_mission.html'
            #     context = {'mission': mission, 'owner': owner}
            #     recipient_list = [owner.email]

            #     send_email(subject, template_name, context, recipient_list)

            messages.success(request, 'Mission created successfully.')
            return redirect('create_mission')  # Adjust the redirect as needed
    else:
        form = MissionForm()

    user_roles = request.user.roles.values_list('name', flat=True)
    return render(request, 'mission/create_mission.html', {'form': form, 'user_roles': user_roles})
#-------------------------------------------------------------------------------------------------

# Assign asset to owner section
def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def assign_asset_owner(request):
    if request.method == 'POST':
        form = AssetOwnerAssignForm(request.POST)
        if form.is_valid():
            owner = form.cleaned_data['owner']
            assets = form.cleaned_data['assets']
            assets.update(owner=owner)
            messages.success(request, 'Assets have been successfully assigned to the owner.')
            return redirect('asset_list')
    else:
        form = AssetOwnerAssignForm()
        
    return render(request, 'mission/assign_asset_owner.html', {'form': form, 'assets': Asset.objects.all()})

@login_required
def asset_list(request):
    assets = Asset.objects.all()
    return render(request, 'mission/asset_list.html', {'assets': assets})
#-------------------------------------------------------------------------------------------------

# close mission section
@login_required
def close_mission(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'Closed'
    mission.save()
    messages.success(request, 'Mission status updated to "Closed".')
    return redirect('mission_detail', mission_id=mission_id)
#-------------------------------------------------------------------------------------------------

# Verification interface
@login_required
def start_verfication(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'In Verification'
    mission.save()
    messages.success(request, 'Mission status updated to "In Verification".')
    return redirect('mission_detail', mission_id=mission_id)

@login_required
def ending_verfication(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'Verified'
    mission.save()
    messages.success(request, 'Mission status updated to "Verified".')
    
    # # Send email to the asset owner
    # asset_owners = {asset.owner for asset in mission.asset if asset.owner}
    # # Create a set to track unique owners
    # unique_owners = set(asset_owners)
    # for owner in unique_owners:
    #     subject = f"the mission with id: {mission.mission_id} have seccesfully completed remediation and verification"
    #     template_name = 'emails/ending_verfication.html'
    #     context = {'mission': mission, 'owner': owner}
    #     recipient_list = [owner.email]

    #     send_email(subject, template_name, context, recipient_list)

    return redirect('mission_detail', mission_id=mission_id)
#-------------------------------------------------------------------------------------------------
