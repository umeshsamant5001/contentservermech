import os
import json
import time
import requests
from pathlib import Path
# from pprint import pprint
from django.shortcuts import render
# from django.views.generic.edit import CreateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import View, TemplateView, ListView
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import (AppAvailableInDB, AppListFromServerData,
                     FileDataToBeStored, JsonDataStorage)

# rest framework imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# command line progress bar import
from clint.textui import progress

#custom imports
from channels.file_downloader import Downloader

# creating object of Downloader class
downloading = Downloader()


# home directory check for every os
homeDir = str(Path.home())

# headers for data fetching
headers = {
    'cache-control': "no-cache",
    'content-type': "application/json; charset=utf-8",
    "Accept": "application/json"
}

channels_result = None

# getting list of channels using API
@login_required
def channel_list_on_server(request):
    # global channels_result
    try:
        context = {}
        channels_url = "http://devposapi.prathamopenschool.org/api/AppList"
        channels_response = requests.get(channels_url, headers=headers)
        channels_result = json.loads(channels_response.content.decode("utf-8"))
        for app in  channels_result:
            for k,v in app.items():
                if k == 'AppName':
                    downloading.download_files_without_qs(channels_url, v)
        context['channels_from_server'] = channels_result
        return render(request, 'channels/channels_list_from_server.html', context=context)
    except requests.exceptions.ConnectionError:
        return HttpResponseRedirect('/channel/no_internet/')


# return the json response in api form for showing checkboxes nad details
@api_view(['GET'])
def return_json_value(request, AppId):
    try:
        url_to_convert = "http://devposapi.prathamopenschool.org/api/AppNode?id={}" .format(
            AppId)
        response_url = requests.get(url_to_convert, headers=headers)
        result_url = json.loads(response_url.content.decode('utf-8'))
        context = {
            'json_data': result_url,
        }
        return Response(context, status=status.HTTP_200_OK)
    except requests.exceptions.ConnectionError:
        return HttpResponseRedirect('/channel/no_internet/')


# showing the page to downlaod the content (jsondata and files)
class ShowDetailsOfChannelView(LoginRequiredMixin, View):
    template_name = "channels/show_details.html"

    def get(self, request, AppId, AppName, *args, **kwargs):
        try:
            context = {}
            print('AppId ', AppId, AppName)
            context['AppId'] = AppId
            context['AppName'] = AppName
            return render(self.request, self.template_name, context=context)
        except requests.exceptions.ConnectionError:
            return HttpResponseRedirect('/channel/no_internet/')


# Downloading and saving the jsondata and files with ids
class DownloadAndSaveView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        node_values = request.POST.getlist('node_values[]')
        AppId = request.POST.get('AppId')
        AppName = request.POST.get('AppName')

        channels_url = "http://devposapi.prathamopenschool.org/api/AppList"
        channels_response = requests.get(channels_url, headers=headers)
        channels_result = json.loads(channels_response.content.decode("utf-8"))

        """ downloading and saving the content from here
            looping through node_values list"""
        # applist_server_data = None
        if not AppListFromServerData.objects.filter(AppId=AppId).exists():
            print(AppId, "server data not in db")
            for apps in channels_result:
                if apps["AppId"] == AppId:
                    applist_local_url = downloading.localUrl
                    applist_local_url = applist_local_url.split('static')[1]
                    # print("local url is ", 'static'+local_url)
                    applist_local_url = 'static'+applist_local_url
                    AppId = apps["AppId"]
                    AppName = apps['AppName']
                    ThumbUrl = apps['ThumbUrl']
                    AppDesc = apps['AppDesc']
                    AppOrder = apps['AppOrder']
                    DateUpdated = apps['DateUpdated']
                    fileName = os.path.basename(ThumbUrl)
                    localUrl = applist_local_url
                    # print("filename", fileName)
                    applist_server_data = AppListFromServerData.objects.create(AppId=AppId, AppName=AppName,
                                                                               ThumbUrl=ThumbUrl, AppDesc=AppDesc,
                                                                               AppOrder=AppOrder, DateUpdated=DateUpdated,
                                                                               fileName=fileName,
                                                                               localUrl=applist_local_url)
                    applist_server_data.save()
        else:
            # just pass the instance of existing app with app id
            applist_server_data = AppListFromServerData.objects.only(
                'AppId').get(AppId=AppId)

        for ids in node_values:
            # hit the detail node each time and get the result
            try:
                detail_node_url = "http://devposapi.prathamopenschool.org/Api/AppNodeDetailListByNode?id={}" .format(
                    ids)
                detail_node_response = requests.get(
                    detail_node_url, headers=headers, timeout=13)
                detail_node_json_val = json.loads(
                    detail_node_response.content.decode('utf-8'))

                # downloading the files
                response_data = downloading.download_files_with_qs(detail_node_url, {"id": ids}, AppName)

                if response_data is False:
                    return HttpResponseRedirect('/channel/no_internet/')
                else:
                    # print("localUrl is ", downloading.localUrl)
                    local_url = downloading.localUrl
                    local_url = local_url.split('static')[1]
                    # print("local url is ", 'static'+local_url)
                    local_url = 'static'+local_url
                    for detail in detail_node_json_val:
                        try:
                            NodeId = detail['NodeId']
                            NodeType = detail['NodeType']
                            NodeTitle = detail['NodeTitle']
                            JsonData = detail['JsonData']
                            ParentId = detail['ParentId']
                            AppId = detail['AppId']
                            DateUpdated = detail['DateUpdated']
                            if not AppAvailableInDB.objects.filter(NodeId=NodeId).exists():
                                app_in_db = AppAvailableInDB.objects.create(applistfromserverdata=applist_server_data,
                                                                            NodeId=NodeId, NodeType=NodeType, NodeTitle=NodeTitle,
                                                                            JsonData=JsonData, ParentId=ParentId,  AppId=AppId,
                                                                            DateUpdated=DateUpdated)
                                app_in_db.save()
                                for file in detail["LstFileList"]:
                                    print("file data is ", file)
                                    FileId = file['FileId']
                                    NodeId = file['NodeId']
                                    FileType = file['FileType']
                                    FileUrl = file['FileUrl']
                                    DateUpdated = file['DateUpdated']
                                    fileName = os.path.basename(FileUrl)
                                    localUrl = local_url
                                    if not FileDataToBeStored.objects.filter(NodeId=NodeId, FileId=FileId).exists():
                                        file_in_db = FileDataToBeStored.objects.create(appavailableindb=app_in_db,
                                                                                        FileId=FileId, NodeId=NodeId,
                                                                                        FileType=FileType, FileUrl=FileUrl,
                                                                                        DateUpdated=DateUpdated, 
                                                                                        fileName=fileName,
                                                                                        localUrl=local_url)
                                        file_in_db.save()

                        except requests.exceptions.ConnectionError:
                            print("db error")
                            return HttpResponseRedirect('/channel/no_internet/')
                
                json_data_storage_view(request, ids)

            except requests.exceptions.ConnectionError:
                print("downlaod error ")
                return HttpResponseRedirect('/channel/no_internet/')

        # return HttpResponse("success!!")
        print("successfully saved!")
        return HttpResponse("success")


def json_data_storage_view(request, id):
    # json_url = "http://fcapp.openiscool.org/api/AppNodeJsonListByNode?id=%s" % id
    json_url = "http://devposapi.prathamopenschool.org/api/AppNodeJsonListByNode?id=%s" % id
    json_response = requests.get(json_url, headers=headers)
    json_result = json.loads(json_response.content.decode("utf-8"))

    try:
        for result in json_result:
            JsonId = result['JsonId']
            NodeId = result['NodeId']
            JsonType = result['JsonType']
            JsonData = result['JsonData']
            DateUpdated = result['DateUpdated']

            if not JsonDataStorage.objects.filter(NodeId=NodeId).exists():
                json_data_storage = JsonDataStorage.objects.create(JsonId=JsonId, NodeId=NodeId, JsonType=JsonType, JsonData=JsonData,
                                                                    DateUpdated=DateUpdated)
                json_data_storage.save()
    
    except requests.exceptions.ConnectionError as con_err:
        print("json error ", con_err)
        return HttpResponseRedirect('/channel/no_internet/')

    return HttpResponse(json_result)


class NoInternetView(TemplateView):
    template_name = 'channels/no_internet.html'


