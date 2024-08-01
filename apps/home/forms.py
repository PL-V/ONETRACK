from django import forms
from .models import Vulnerability, Asset, Mission
from ..authentication.models import User

class VulnerabilityForm(forms.ModelForm):
    asset = forms.ModelChoiceField(queryset=Asset.objects.all(), label="Asset")

    class Meta:
        model = Vulnerability
        fields = ['vuln_name', 'vuln_type', 'vuln_severity', 'vuln_description', 'cve', 'risk', 'source', 'asset']
        labels = {
            'vuln_name': 'Vulnerability Name',
            'vuln_type': 'Vulnerability Type',
            'vuln_severity': 'Vulnerability Severity',
            'vuln_description': 'Vulnerability Description',
            'cve': 'CVE',
            'risk': 'Risk',
            'source': 'Source',
        }



class MissionStatusForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['state']
        widgets = {
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mission status'}),
        }


class MissionAssignForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(queryset=User.objects.filter(role='Remediator'), label="Assign to Remediator")

    class Meta:
        model = Mission
        fields = ['assigned_to']