from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('programs/', views.program_call, name='programs'),
    path('states/', views.state_call, name='states'),
    path('districts/', views.district_call, name='districts'),
    path('blocks/', views.block_call, name='blocks'),
    path('villages/', views.show_villages, name='villages'),
    path('post_all_data/', views.post_all_data, name='post_all_data'),
    path('users/', views.user_register, name='users'),
]
