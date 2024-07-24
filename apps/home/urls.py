# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    #additionnal paths
    path('vulnerabilities/', views.vulnerability_list, name='vulnerability_list'),
    path('report_vulnerability/', views.report_vulnerability, name='report_vulnerability'),
    # path('vulnerabilities/assign/<int:id>/', views.assign_vulnerability, name='assign_vulnerability'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]

