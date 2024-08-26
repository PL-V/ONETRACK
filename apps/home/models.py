from django.db import models
from ..authentication.models import User
import uuid

class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_name = models.CharField(max_length=255)
    asset_category = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_assets', null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    site = models.CharField(max_length=255)
    classification = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)

    class Meta:
        db_table = 'asset'
    
    def __str__(self):
        return self.asset_name


class Vulnerability(models.Model):
    vuln_id = models.AutoField(primary_key=True)
    mapping_id = models.CharField(max_length=255)
    vuln_name = models.CharField(max_length=255)
    vuln_type = models.CharField(max_length=255)
    vuln_severity = models.CharField(max_length=255)
    vuln_description = models.TextField()
    cve = models.CharField(max_length=255)
    risk = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    reported_by = models.ForeignKey(User, related_name='reported_vulnerabilities', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='assigned_vulnerabilities', on_delete=models.CASCADE, null=True, blank=True)
    verified_by = models.ForeignKey(User, related_name='verified_vulnerabilities', on_delete=models.CASCADE, null=True, blank=True)
    asset = models.ManyToManyField(Asset)

    class Meta:
        db_table = 'vulnerability'


class Mission(models.Model):
    status_choices = [
        ('Reported', 'Reported'),
        ('Assigned', 'Assigned'),
        ('In Remediation', 'In Remediation'),
        ('Remediated', 'Remediated'),
        ('In Verification', 'In Verification'),
        ('Verified', 'Verified'),
        ('Closed', 'Closed'),
    ]
    mission_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=status_choices, null=True)
    asset = models.ManyToManyField(Asset)
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE)
    priority = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    closed_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'mission'


class MissionHistory(models.Model):
    mission_history_id = models.AutoField(primary_key=True)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    change_date = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('Reported', 'Reported'),
        ('Assigned', 'Assigned'),
        ('In Remediation', 'In Remediation'),
        ('Remediated', 'Remediated'),
        ('In Verification', 'In Verification'),
        ('Verified', 'Verified'),
        ('Closed', 'Closed'),
    ]
    state_on_change_date = models.CharField(max_length=40, choices=status_choices)

    class Meta:
        db_table = 'mission_history'

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'


class Metric(models.Model):
    metric_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    value = models.FloatField()
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'metric'


class ScrapedVulnerability(models.Model):
    vuln_id = models.AutoField(primary_key=True)
    vuln_name = models.CharField(max_length=255,null=True, blank=True)
    vuln_type = models.CharField(max_length=255,null=True, blank=True)
    vuln_severity = models.CharField(max_length=255,null=True, blank=True)
    vuln_description = models.TextField()
    cve = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.vuln_name
    
    class Meta:
        db_table = 'scraped_vulnerability'