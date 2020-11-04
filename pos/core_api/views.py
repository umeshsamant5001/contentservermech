# python and django imports
import os
import json
import string
import random
import platform
import datetime
from pathlib import Path

# rest framework imports
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

#  filters import
# import django_filters.rest_framework
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# local imports
from core.models import VillageDataStore, UsageData
from .serializers import VillageDataStoreSerializer, UsageDataSerializer

N = 6
# homeDir = ''

class VillageDataStoreView(viewsets.ModelViewSet):
    queryset = VillageDataStore.objects.order_by('id')
    serializer_class = VillageDataStoreSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filter_fields = ('filter_name', 'table_name', 'key_id')
    pagination_class = PageNumberPagination


class UsageDataView(viewsets.ModelViewSet):
    model = UsageData
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    queryset = UsageData.objects.all()
    serializer_class = UsageDataSerializer
    filter_fields = ('filter_name', 'table_name')
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

        system_os = platform.system()
        # print("os is ", system_os)

        def save_in_folder():
            if system_os == "Windows":
                homeDir = r"C:\prathambackupdata\AutoDataBackup"
                path = os.path.isdir(homeDir)
                if path is False:
                    os.makedirs(homeDir)
                
                if serializer.data['table_name'] == 'USAGEDATA':
                    data = serializer.data['data']
                    filter_name = serializer.data['filter_name']
                    table_name = serializer.data['table_name']
                    
                    json_data_to_save = {
                        "data": str(data).encode("ascii", "replace").decode(),
                        "filter_name": filter_name.encode("ascii", "replace").decode(),
                        "table_name": table_name.encode("ascii", "replace").decode(),
                    }

                    randstr = ''.join(random.choice(
                        string.ascii_uppercase + string.digits) for _ in range(N))
                    with open(os.path.join(homeDir,
                                           randstr+'.json'), "w+") as outfile:
                        json.dump(json_data_to_save, outfile,
                                  indent=4, sort_keys=True)

            else:
                homeDir = str(Path.home())
                homeDir = os.path.join(homeDir, 'prathambackupdata/AutoDataBackup')
                if not os.path.exists(homeDir):
                    os.makedirs(homeDir)

                if serializer.data['table_name'] == 'USAGEDATA':
                    data = serializer.data['data']
                    filter_name = serializer.data['filter_name']
                    table_name = serializer.data['table_name']
                    
                    json_data_to_save = {
                        "data": str(data).encode("ascii", "replace").decode(),
                        "filter_name": filter_name.encode("ascii", "replace").decode(),
                        "table_name": table_name.encode("ascii", "replace").decode(),
                    }
                    randstr = ''.join(random.choice(
                        string.ascii_uppercase + string.digits) for _ in range(N))
                    with open(os.path.join(homeDir, randstr+str(datetime.datetime.now())+'.json'), "w+") as outfile:
                        json.dump(json_data_to_save, outfile,
                                    indent=4, sort_keys=True)

        save_in_folder()

        def show_data():
            if system_os == "Windows":
                homeDir = r"C:\prathambackupdata\AutoSummaryBackup"
                path = os.path.isdir(homeDir)
                if path is False:
                    os.makedirs(homeDir)
                else:
                    pass
            else:
                homeDir = str(Path.home())
                homeDir = os.path.join(homeDir, 'prathambackupdata/AutoSummaryBackup')
                if not os.path.exists(homeDir):
                    os.makedirs(homeDir)
                else:
                    pass

            if serializer.data['table_name'] == 'USAGEDATA':
                device_id = serializer.data['data']['metadata']['DeviceId']
                serial_id = serializer.data['data']['metadata']['SerialID']
                app_name = serializer.data['data']['metadata']['appName']
                apk_version = serializer.data['data']['metadata']['apkVersion']
                score_count = serializer.data['data']['metadata']['ScoreCount']
                pratham_code = serializer.data['data']['metadata']['prathamCode']
                device_name = serializer.data['data']['metadata']['DeviceName']

                now = datetime.datetime.now()

                view_to_crl = {
                    "device_id": str(device_id).encode("ascii", "replace").decode(),
                    "serial_id": serial_id.encode("ascii", "replace").decode(),
                    "app_name": app_name.encode("ascii", "replace").decode(),
                    "apk_version": apk_version.encode("ascii", "replace").decode(),
                    "score_count": score_count,
                    "pratham_code": pratham_code.encode("ascii", "replace").decode(),
                    "device_name": device_name.encode("ascii", "replace").decode(),
                    "date": now.strftime("%Y-%m-%d %H:%M:%S")
                }

                view_to_crl = str(view_to_crl).encode(
                    "ascii", "replace").decode()

                try:
                    with open(os.path.join(homeDir, 'score_data.json'), "a") as newfile:
                        newfile.writelines(
                            view_to_crl.encode().decode()+",")
                        newfile.write("\n")
                except FileNotFoundError as e:
                    print(e)

        show_data()

# csrfmiddlewaretoken