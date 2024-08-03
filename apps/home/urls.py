from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    # path('', views.index, name='home'),
    path('', views.mission_list, name='mission_list'),

    #additionnal paths
    path('vulnerabilities/', views.vulnerability_list, name='vulnerability_list') ,
    
    path('report_vulnerability/', views.report_vulnerability, name='report_vulnerability'),
    
    path('missions/', views.mission_list, name='mission_list'),
    path('missions/<uuid:id>/', views.mission_detail, name='mission_detail'),
    path('missions/update_status/<uuid:id>/', views.update_mission_status, name='update_mission_status'),
    path('missions/assign/<uuid:id>/', views.assign_mission, name='assign_mission'),
    path('assigned_vulnerabilities/', views.assigned_vulnerabilities, name='assigned_vulnerabilities'),
    path('missions/remediator/<uuid:id>/', views.mission_detail_for_remediator, name='mission_detail_for_remediator'),
    
    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

]

