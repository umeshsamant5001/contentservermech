# rest framework imports
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

# filters import
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# local imports
from channels.models import (AppListFromServerData, AppAvailableInDB,
                             FileDataToBeStored, FileUpload, JsonDataStorage)
from .serializers import (AppListSerializer, AppAvailableSerializer,
                          FileDataSerializer, AppNodeDetailListSerializer,
                          FileUploadSerializer, JsonDataStorageSerializer)


class AppView(viewsets.ModelViewSet):
    # queryset = AppListFromServerData.objects.order_by('AppId')
    serializer_class = AppListSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    # filter_fields = ('AppId', 'AppName')
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = AppListFromServerData.objects.all().order_by('AppId')
        # print('queryset is', queryset)
        app_id = self.request.query_params.get('AppId', None)
        app_name = self.request.query_params.get('AppName', None)
        if app_id and app_name:
            queryset1 = queryset.filter(Q(AppId__iexact=app_id) & Q(AppName__iexact=app_name))
            # print('queryset1 is', queryset1)
            return queryset1
        elif app_id:
            queryset2 = queryset.filter(AppId__iexact=app_id)
            # print('queryset2 is', queryset2)
            return queryset2
        elif app_name:
            queryset2 = queryset.filter(AppName__iexact=app_name)
            # print('queryset2 is', queryset2)
            return queryset2
        return queryset


class AppAvailableView(viewsets.ModelViewSet):
    # queryset = AppAvailableInDB.objects.all()
    serializer_class = AppAvailableSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    # filter_fields = ('AppId', 'NodeType')
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = AppAvailableInDB.objects.all().order_by('AppId')
        # print('queryset is', queryset)
        app_id = self.request.query_params.get('AppId', None)
        node_type = self.request.query_params.get('NodeType', None)
        if app_id and node_type:
            queryset1 = queryset.filter(Q(AppId__iexact=app_id) & Q(NodeType__iexact=node_type))
            # print('queryset1 is', queryset1)
            return queryset1
        elif app_id:
            queryset2 = queryset.filter(AppId__iexact=app_id)
            # print('queryset2 is', queryset2)
            return queryset2
        elif node_type:
            queryset2 = queryset.filter(NodeType__iexact=node_type)
            # print('queryset2 is', queryset2)
            return queryset2
        return queryset
        

class AppNodeDetailListByNodeView(viewsets.ModelViewSet):
    queryset = AppAvailableInDB.objects.all().order_by('NodeId')
    serializer_class = AppNodeDetailListSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('NodeId', 'AppId',)
    pagination_class = PageNumberPagination


class FileUploadView(viewsets.ModelViewSet):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(uploaded_file=self.request.data.get('uploaded_file'))


class JsonDataStorageView(viewsets.ModelViewSet):
    queryset = JsonDataStorage.objects.all()
    serializer_class = JsonDataStorageSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('NodeId', 'JsonType',)
    pagination_class = PageNumberPagination
