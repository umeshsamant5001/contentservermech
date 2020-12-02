from django.urls import path, re_path
from . import views

app_name = 'content_viewer'

urlpatterns = [
    path('app_available/', views.AppAvailableListView.as_view(), name='app_available'),
    path('parent_details/<str:AppId>/', views.ParentAppView.as_view(), name='parent_details'),
    path('child_details/<str:NodeId>/', views.ChildrenAppView.as_view(), name='child_details'),
    path('resource/<str:NodeId>/', views.resource_view, name='resource'),
    path('score/', views.desktop_score_data, name='score'),
    
]