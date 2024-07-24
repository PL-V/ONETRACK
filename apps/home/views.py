from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Vulnerability
from django.shortcuts import render, redirect
from .forms import VulnerabilityForm


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        # Log the error or print a message for debugging
        print(f"Template {load_template} does not exist.")
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        # Log the error or print a message for debugging
        print(f"An error occurred: {e}")
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

    

@login_required
def vulnerability_list(request):
    vulnerabilities = Vulnerability.objects.all()
    return render(request, 'mission/vulnerabilityList.html', {'vulnerabilities': vulnerabilities})



@login_required
def report_vulnerability(request):
    if request.method == 'POST':
        form = VulnerabilityForm(request.POST)
        if form.is_valid():
            vulnerability = form.save(commit=False)
            vulnerability.reported_by = request.user
            vulnerability.save()
            return redirect('vulnerability_list')
    else:
        form = VulnerabilityForm(initial={'reported_by': request.user})
    return render(request, 'mission/report.html', {'form': form})