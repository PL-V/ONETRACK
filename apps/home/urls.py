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
    path('missions/<uuid:mission_id>/', views.mission_detail, name='mission_detail'),
    path('missions/assign/<uuid:mission_id>/', views.assign_mission, name='assign_mission'),
    path('create_mission/', views.create_mission, name='create_mission'),
    path('missions/start_remediation/<uuid:mission_id>/', views.start_remediation, name='start_remediation'),
    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

]

