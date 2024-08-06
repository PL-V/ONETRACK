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
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=Mission.status_choices)
        }

class MissionAssignForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(queryset=User.objects.filter(roles__name='Remediator'), label="Assign to Remediator")

    class Meta:
        model = Mission
        fields = ['assigned_to']


class MissionForm(forms.Form):
    vuln_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    vuln_type = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    vuln_severity = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    vuln_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    cve = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    risk = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    source = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    assets = forms.ModelMultipleChoiceField(queryset=Asset.objects.all(), widget=forms.CheckboxSelectMultiple)