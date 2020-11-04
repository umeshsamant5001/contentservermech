from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register('AppList', views.AppView, basename='AppList')
router.register('AppNode', views.AppAvailableView, basename='AppNode')
router.register('AppNodeDetailListByNode', views.AppNodeDetailListByNodeView,
                basename='AppNodeDetailListByNode')
router.register('FileUpload', views.FileUploadView, basename='FileUpload')


urlpatterns = [
    path('', include(router.urls)),
]
