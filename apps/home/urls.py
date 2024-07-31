from django.urls import path, re_path
from apps.home import views

print('in urls')
urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    #additionnal paths
    path('vulnerabilities/', views.vulnerability_list, name='vulnerability_list') ,
    
    path('report_vulnerability/', views.report_vulnerability, name='report_vulnerability'),
    
    path('missions/', views.mission_list, name='mission_list'),
    path('missions/<uuid:id>/', views.mission_detail, name='mission_detail'),
    path('missions/update_status/<uuid:id>/', views.update_mission_status, name='update_mission_status'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]

