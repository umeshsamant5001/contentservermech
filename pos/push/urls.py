from django.urls import path
from . import views

app_name = 'push'

urlpatterns = [
    path('', views.push_data, name="push-data"),
    path('usage/', views.push_usageData, name="usage"),
    path('backup/', views.backup, name="backup"),
]

