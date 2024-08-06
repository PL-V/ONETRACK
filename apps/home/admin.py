from django.contrib import admin
from .models import (
    Asset, Vulnerability, Mission, MissionHistory,
    Notification, Metric, ComponentType, Component
)


admin.site.register(Asset)
admin.site.register(Vulnerability)
admin.site.register(Mission)
admin.site.register(MissionHistory)
admin.site.register(Notification)
admin.site.register(Metric)
admin.site.register(ComponentType)
admin.site.register(Component)
