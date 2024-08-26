from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Vulnerability, Mission, MissionHistory, Asset, Metric, ScrapedVulnerability
from .forms import MissionAssignForm,  MissionForm, AssetOwnerAssignForm, VerificationOutcomeForm
from .utils import send_email 
from .utils import calculate_metrics
from django.db.models import Q
from .services import TextSimilarityService



#-------------------------------------------------------------------------------------------------
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
                # due_date=timezone.now().date(),
                vulnerability=vulnerability
            )
            mission.asset.set(assets)  

            # Create initial mission history
            MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                change_date = timezone.now().date(),
                state_on_change_date = mission.status
            )
            
            # Send email to the asset owner
            asset_owners = {asset.owner for asset in mission.asset.all() if asset.owner}
            # Create a set to track unique owners
            unique_owners = set(asset_owners)
            subject = "New Mission Reported"
            template_name = 'emails/new_mission.html'
            mission_link = f"http://127.0.0.1:8000/missions/{mission.mission_id}"
            for owner in unique_owners:
                context = {'mission': mission, 'owner': owner, 'mission_link':mission_link}
                recipient_list = [owner.email]

                send_email(subject, template_name, context, recipient_list)

            messages.success(request, 'Mission created successfully.')
            return redirect('create_mission')  # Adjust the redirect as needed
    else:
        form = MissionForm()

    user_roles = request.user.roles.values_list('name', flat=True)
    return render(request, 'mission/create_mission.html', {'form': form, 'user_roles': user_roles})
#-------------------------------------------------------------------------------------------------

# Mission List Section
@login_required
def mission_list(request):
    user_roles = request.user.roles.values_list('name', flat=True)
    if request.user.is_superuser:
        missions = Mission.objects.exclude(status='Closed')
    elif 'Owner' in user_roles:
        missions = Mission.objects.filter(
            asset__owner=request.user
        ).exclude(status='Closed').distinct()
    elif 'Remediator' in user_roles:
        missions = Mission.objects.filter(
            vulnerability__assigned_to=request.user,
            status__in=['In Remediation', 'Assigned']
        ).distinct()
    elif 'Verifier' in user_roles:
        missions = Mission.objects.filter(
            Q(status='Remediated') | 
            (Q(status='In Verification') & Q(vulnerability__verified_by=request.user))
        ).exclude(status='Closed')
    else:
        missions = Mission.objects.exclude(status='Closed')
    
    context = {
        'missions': missions,
        'user_roles': user_roles
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
            MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                change_date = timezone.now().date(),
                state_on_change_date = mission.status
            )

            # # Send email to the Remediated
            # subject = f"A new mission has been assigned to you"
            # template_name = 'emails/assign_mission.html'
   
            # full_mission_link = f"http://127.0.0.1:8000/missions/{mission.mission_id}"
            # context = {'mission': mission, 'assigned_user': assigned_user, 'mission_link':full_mission_link}
            # recipient_list = [assigned_user.email]
            # send_email(subject, template_name, context, recipient_list)
            
            messages.success(request, 'Mission assigned successfully.')
            return redirect('assign_mission', mission_id=mission_id)
    else:
        form = MissionAssignForm(instance=mission)
    
    return render(request, 'mission/assign_mission.html', {'form': form, 'mission': mission})
#-------------------------------------------------------------------------------------------------

# Remediation section
@login_required
def start_remediation(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'In Remediation'
    mission.save()
    messages.success(request, 'Mission status updated to "In Remediation".')
    MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                change_date = timezone.now().date(),
                state_on_change_date = mission.status
    )
    return redirect('mission_detail', mission_id=mission_id)

@login_required
def ending_remediation(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'Remediated'
    mission.save()
    MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                change_date = timezone.now().date(),
                state_on_change_date = mission.status
    )
    messages.success(request, 'Mission status updated to "Remediated".')
    # # Send email to the asset owner
    # verifiers = User.objects.filter(roles__name = 'Verifier')
    # subject = "New Mission Reported"
    # template_name = 'emails/new_mission.html'
    # mission_link = f"http://127.0.0.1:8000/missions/{mission.mission_id}"
    # for verifier in verifiers:
    #     context = {'mission': mission, 'verifier': verifier, 'mission_link':mission_link}
    #     recipient_list = [verifier.email]

    #     send_email(subject, template_name, context, recipient_list)

    return redirect('mission_detail', mission_id=mission_id)
#-------------------------------------------------------------------------------------------------

# Verification interface
@login_required
def start_verification(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'In Verification'
    mission.save()
    mission.vulnerability.verified_by = request.user
    mission.vulnerability.save()
    MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                change_date = timezone.now().date(),
                state_on_change_date = mission.status
    )
    messages.success(request, 'Mission status updated to "In Verification".')
    return redirect('mission_detail', mission_id=mission_id)

@login_required
def ending_verification(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    
    if request.method == 'POST':
        form = VerificationOutcomeForm(request.POST)
        if form.is_valid():
            outcome = form.cleaned_data['outcome']
            issue_description = form.cleaned_data.get('issue_description', '')

            if outcome == 'successful':
                mission.status = 'Verified'
                messages.success(request, 'Mission status updated to "Verified".')

                # # Send email to the asset owners
                # asset_owners = {asset.owner for asset in mission.asset.all() if asset.owner}
                # unique_owners = set(asset_owners)
                # subject = "Mission verification status"
                # template_name = 'emails/ending_verification.html'
                # mission_link = f"http://127.0.0.1:8000/missions/{mission.mission_id}"
                # for owner in unique_owners:
                #     context = {
                #         'mission': mission, 
                #         'owner': owner, 
                #         'mission_link': mission_link
                #     }
                #     recipient_list = [owner.email]
                #     send_email(subject, template_name, context, recipient_list)

            else:
                mission.status = 'Reported'
                messages.warning(request, 'Verification ended with a problem.')

                # # Send email to the asset owners
                # asset_owners = {asset.owner for asset in mission.asset.all() if asset.owner}
                # unique_owners = set(asset_owners)
                # subject = "Mission verification status"
                # template_name = 'emails/ending_verification.html'
                # mission_link = f"http://127.0.0.1:8000/missions/{mission.mission_id}"
                # for owner in unique_owners:
                #     context = {
                #         'mission': mission, 
                #         'owner': owner, 
                #         'mission_link': mission_link,
                #         'issue_description': issue_description
                #     }
                #     recipient_list = [owner.email]
                #     send_email(subject, template_name, context, recipient_list)

            mission.save()
            MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                change_date = timezone.now().date(),
                state_on_change_date = mission.status
            )                
            return redirect('ending_verification', mission_id=mission_id)
    else:
        form = VerificationOutcomeForm()
    
    return render(request, 'mission/verification_outcome.html', {'form': form, 'mission': mission})
#-------------------------------------------------------------------------------------------------

# close mission section
@login_required
def close_mission(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    mission.status = 'Closed'
    mission.closed_date= timezone.now().date()
    mission.save()
    MissionHistory.objects.create(
                mission=mission,
                user=request.user,
                change_date = timezone.now().date(),
                state_on_change_date = mission.status
    )
    messages.success(request, 'Mission status updated to "Closed".')

    # Notify All:
    # Notify verifiers
    # subject = "New Mission Closed"
    # template_name = 'emails/ending_mission.html'

    # verifiers = User.objects.filter(roles__name = 'Verifier')
    # for verifier in verifiers:
        
    #     context = {'mission': mission, 'userToNotify': verifier}
    #     recipient_list = [verifier.email]

    #     send_email(subject, template_name, context, recipient_list)

    # # Notify Owners
    # owners = {asset.owner for asset in mission.vulnerability.asset if asset.owner}
    # for owner in owners:
    #     context = {'mission': mission, 'userToNotify': owner}
    #     recipient_list = [owner.email]

    #     send_email(subject, template_name, context, recipient_list)

    # # Notify Remediator
    # assign_remediator = mission.vulnerability.assigned_to
    # context = {'mission': mission, 'userToNotify': assign_remediator}
    # recipient_list = [assign_remediator.email]
    # send_email(subject, template_name, context, recipient_list)

    return redirect('mission_detail', mission_id=mission_id)
#-------------------------------------------------------------------------------------------------

# Metric Section
@login_required
def metrics_dashboard(request):
    # Calculate metrics
    metrics = calculate_metrics()
    
    for metric in metrics:
        # Check if the metric already exists
        existing_metric = Metric.objects.filter(name=metric.name, mission=metric.mission).first()
        
        if existing_metric:
            # Update the existing metric's value
            existing_metric.value = metric.value
            existing_metric.save()
        else:
            # If it doesn't exist, create a new metric
            metric.save()

    # Retrieve all metrics to display in the dashboard
    saved_metrics = Metric.objects.all()

    return render(request, 'metrics/dashboard.html', {'metrics': saved_metrics})
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
#-------------------------------------------------------------------------------------------------

# Assets listing
@login_required
def asset_list(request):
    assets = Asset.objects.all()
    return render(request, 'mission/asset_list.html', {'assets': assets})
#-------------------------------------------------------------------------------------------------

# Recommandations 
@login_required
def search_similar_vulnerabilities(request):
    if request.method == 'POST':
        user_input = request.POST.get('description')
        vulnerabilities = ScrapedVulnerability.objects.all()
        similarity_service = TextSimilarityService()
        similar_vulnerabilities = similarity_service.find_similar_descriptions(user_input, vulnerabilities)

        context = {
            'similar_vulnerabilities': similar_vulnerabilities,
            'user_input': user_input
        }
        return render(request, 'recommandations/similar_vulnerabilities.html', context)
    return render(request, 'recommandations/search_form.html')
#-------------------------------------------------------------------------------------------------