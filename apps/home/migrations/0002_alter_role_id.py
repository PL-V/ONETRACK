# Generated by Django 5.0.6 on 2024-07-24 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
