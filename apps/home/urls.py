from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.mission_list, name='mission_list'),

    #additionnal paths
    path('missions/', views.mission_list, name='mission_list'),
    path('missions/<uuid:mission_id>/', views.mission_detail, name='mission_detail'),

    path('create_mission/', views.create_mission, name='create_mission'),

    path('missions/assign/<uuid:mission_id>/', views.assign_mission, name='assign_mission'),
    
    path('missions/start_remediation/<uuid:mission_id>/', views.start_remediation, name='start_remediation'),
    path('missions/ending_remediation/<uuid:mission_id>/', views.ending_remediation, name='ending_remediation'),



    path('missions/start_verification/<uuid:mission_id>/', views.start_verification, name='start_verification'),
    path('missions/ending_verification/<uuid:mission_id>/', views.ending_verification, name='ending_verification'),

    path('missions/close_mission/<uuid:mission_id>/', views.close_mission, name='close_mission'),

    path('assign_asset_owner/', views.assign_asset_owner, name='assign_asset_owner'),
    path('assets/', views.asset_list, name='asset_list'),
    path('dashboard/', views.metrics_dashboard, name='metrics_dashboard'),

    path('search/', views.search_similar_vulnerabilities, name='search_similar_vulnerabilities'),
]



