from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Metric, Mission, Asset


def send_email(subject, template_name, context, recipient_list):
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

def calculate_metrics():
    metrics = []

    # Missions in progress
    missions_in_progress = Mission.objects.exclude(status='Closed').count()
    metrics.append(Metric(name='Missions in progress', value=missions_in_progress))

    # Active vulnerable assets
    active_vulnerable_assets = Asset.objects.filter(
        mission__status__in=['Reported', 'Assigned', 'In Remediation', 'Remediated', 'In Verification', 'Verified']
    ).distinct().count()
    metrics.append(Metric(name='Active vulnerable assets', value=active_vulnerable_assets))

    # Non-vulnerable assets (%)
    total_assets = Asset.objects.count()
    non_vulnerable_assets = total_assets - active_vulnerable_assets
    non_vulnerable_percentage = (non_vulnerable_assets / total_assets) * 100 if total_assets else 0
    metrics.append(Metric(name='Non vulnerable assets (%)', value=non_vulnerable_percentage))

    # Mean Time to Remediate (MTTR)
    remediation_times = [
        (mission.closed_date - mission.created_date).total_seconds() 
        for mission in Mission.objects.filter(closed_date__isnull=False)
    ]
    mean_time_to_remediate = sum(remediation_times) / len(remediation_times) if remediation_times else 0
    metrics.append(Metric(name='Mean Time to Remediate (MTTR)', value=mean_time_to_remediate))

    # Time to Remediate (TTR) by mission
    for mission in Mission.objects.filter(closed_date__isnull=False):
        ttr = (mission.closed_date - mission.created_date).total_seconds()
        metrics.append(Metric(name=f'TTR for mission {mission.mission_id}', value=ttr, mission=mission))

    return metrics