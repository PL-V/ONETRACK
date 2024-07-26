from django.db import models
import uuid
from ..authentication.models import User


class Asset(models.Model):
    asset_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_name = models.CharField(max_length=255)
    asset_category = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    site = models.CharField(max_length=255)
    classification = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)

    class Meta:
        db_table = 'asset'

class Vulnerability(models.Model):
    vuln_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    class Meta:
        db_table = 'vulnerability'

class Mission(models.Model):
    mission_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=255)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE)
    priority = models.CharField(max_length=255)
    due_date = models.DateField()
    created_date = models.DateField(auto_now_add=True)
    closed_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'mission'

class MissionHistory(models.Model):
    mission_history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    change_date = models.DateTimeField(auto_now_add=True)
    state_on_change_date = models.CharField(max_length=255)

    class Meta:
        db_table = 'mission_history'

class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'

class Metric(models.Model):
    metric_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    value = models.FloatField()
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'metric'

class Status(models.Model):
    id = models.BigAutoField(primary_key=True)
    status_choices = [
        ('Reported', 'Reported'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Remediated', 'Remediated'),
        ('Verified', 'Verified'),
        ('Closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)

    class Meta:
        db_table = 'status'

class ComponentType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=255)

    class Meta:
        db_table = 'component_type'

class Component(models.Model):
    component_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    component_type = models.ForeignKey(ComponentType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)

    class Meta:
        db_table = 'component'

class AttackMapping(models.Model):
    attack_mapping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exploit_type = models.CharField(max_length=255)
    primary_impact = models.IntegerField()
    secondary_impact = models.IntegerField()

    class Meta:
        db_table = 'attack_mapping'
