from django.urls import path
from . import views


urlpatterns = [
    path('', views.push_data, name="push_data"),]

