# Generated by Django 5.0.6 on 2024-07-26 22:37

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttackMapping',
            fields=[
                ('attack_mapping_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('exploit_type', models.CharField(max_length=255)),
                ('primary_impact', models.IntegerField()),
                ('secondary_impact', models.IntegerField()),
            ],
            options={
                'db_table': 'attack_mapping',
            },
        ),
        migrations.CreateModel(
            name='ComponentType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'component_type',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('Reported', 'Reported'), ('Assigned', 'Assigned'), ('In Progress', 'In Progress'), ('Remediated', 'Remediated'), ('Verified', 'Verified'), ('Closed', 'Closed')], max_length=20)),
            ],
            options={
                'db_table': 'status',
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('asset_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('asset_name', models.CharField(max_length=255)),
                ('asset_category', models.CharField(max_length=255)),
                ('asset_type', models.CharField(max_length=255)),
                ('ip_address', models.GenericIPAddressField()),
                ('site', models.CharField(max_length=255)),
                ('classification', models.CharField(max_length=255)),
                ('platform', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('serial_number', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'asset',
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('component_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.asset')),
                ('component_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.componenttype')),
            ],
            options={
                'db_table': 'component',
            },
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('mission_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('state', models.CharField(max_length=255)),
                ('priority', models.CharField(max_length=255)),
                ('due_date', models.DateField()),
                ('created_date', models.DateField(auto_now_add=True)),
                ('closed_date', models.DateField(blank=True, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.asset')),
            ],
            options={
                'db_table': 'mission',
            },
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('metric_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('value', models.FloatField()),
                ('mission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.mission')),
            ],
            options={
                'db_table': 'metric',
            },
        ),
        migrations.CreateModel(
            name='MissionHistory',
            fields=[
                ('mission_history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('change_date', models.DateTimeField(auto_now_add=True)),
                ('state_on_change_date', models.CharField(max_length=255)),
                ('mission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.mission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mission_history',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('message', models.TextField()),
                ('sent_date', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notification',
            },
        ),
        migrations.CreateModel(
            name='Vulnerability',
            fields=[
                ('vuln_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mapping_id', models.CharField(max_length=255)),
                ('vuln_name', models.CharField(max_length=255)),
                ('vuln_type', models.CharField(max_length=255)),
                ('vuln_severity', models.CharField(max_length=255)),
                ('vuln_description', models.TextField()),
                ('cve', models.CharField(max_length=255)),
                ('risk', models.CharField(max_length=255)),
                ('source', models.CharField(max_length=255)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.asset')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_vulnerabilities', to=settings.AUTH_USER_MODEL)),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported_vulnerabilities', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='verified_vulnerabilities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'vulnerability',
            },
        ),
        migrations.AddField(
            model_name='mission',
            name='vulnerability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.vulnerability'),
        ),
    ]
