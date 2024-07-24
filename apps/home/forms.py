from django import forms
from .models import Vulnerability, User, Asset

class VulnerabilityForm(forms.ModelForm):
    reported_by = forms.ModelChoiceField(queryset=User.objects.all(), label="Reported By")
    asset = forms.ModelChoiceField(queryset=Asset.objects.all(), label="Asset")

    class Meta:
        model = Vulnerability
        fields = ['vuln_name', 'vuln_type', 'vuln_severity', 'vuln_description', 'cve', 'risk', 'source', 'reported_by', 'asset']
        labels = {
            'vuln_name': 'Vulnerability Name',
            'vuln_type': 'Vulnerability Type',
            'vuln_severity': 'Vulnerability Severity',
            'vuln_description': 'Vulnerability Description',
            'cve': 'CVE',
            'risk': 'Risk',
            'source': 'Source',
        }