from django.urls import path
from . import views


app_name = 'channels'


urlpatterns = [
    path('channel_list/', views.channel_list_on_server, name='channel_list'),
    path('return_json_value/<str:AppId>/', views.return_json_value, name='return_json_value'),
    path('show_details/<str:AppId>/<str:AppName>/', views.ShowDetailsOfChannelView.as_view(), 
        name='show_details'),
    path('downloads/', views.DownloadAndSaveView.as_view(), name='downloads'),
    path('json_data/<str:id>/', views.json_data_storage_view, name='json_data'),
    path('no_internet/', views.NoInternetView.as_view(), name='no_internet'),
]