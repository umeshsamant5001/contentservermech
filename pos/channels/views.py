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
from .models import AppAvailableInDB, AppListFromServerData, FileDataToBeStored

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
    'content-type': "application/json",
    "Accept": "application/json"
}

channels_result = None

# getting list of channels using API
@login_required
def channel_list_on_server(request):
    global channels_result
    try:
        context = {}
        channels_url = "http://devposapi.prathamopenschool.org/api/AppList"
        channels_response = requests.get(channels_url, headers=headers)
        channels_result = json.loads(channels_response.content.decode("utf-8"))
        downloading.download_files_without_qs(channels_url)
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
        # node_values1 = list(map(str, node_values))
        AppId = request.POST.get('AppId')

        """ downloading and saving the content from here
            looping through node_values list"""
        # applist_server_data = None
        if not AppListFromServerData.objects.filter(AppId=AppId).exists():
            print(AppId, "server data not in db")
            for apps in channels_result:
                if apps["AppId"] == AppId:
                    print("aps is : ", apps)
                    AppId = apps["AppId"]
                    AppName = apps['AppName']
                    ThumbUrl = apps['ThumbUrl']
                    AppDesc = apps['AppDesc']
                    AppOrder = apps['AppOrder']
                    DateUpdated = apps['DateUpdated']
                    fileName = os.path.basename(ThumbUrl)
                    print("filename", fileName)
                    applist_server_data = AppListFromServerData.objects.create(AppId=AppId, AppName=AppName,
                                                                               ThumbUrl=ThumbUrl, AppDesc=AppDesc,
                                                                               AppOrder=AppOrder, DateUpdated=DateUpdated,
                                                                               fileName=fileName)
                    applist_server_data.save()
        else:
            # just pass the instance of existing app with app id
            applist_server_data = AppListFromServerData.objects.only(
                'AppId').get(AppId=AppId)

        for ids in node_values:
            # hit the detail node each time and get the result
            try:
                # print(ids)
                detail_node_url = "http://devposapi.prathamopenschool.org/Api/AppNodeDetailListByNode?id={}" .format(
                    ids)
                detail_node_response = requests.get(
                    detail_node_url, headers=headers, timeout=13)
                detail_node_json_val = json.loads(
                    detail_node_response.content.decode('utf-8'))

                # downloading the files
                response_data = downloading.download_files_with_qs(detail_node_url, {"id": ids})

                if response_data is False:
                    print("it is false")
                    return HttpResponseRedirect('/channel/no_internet/')
                else:
                    print("it is true")
                    for detail in detail_node_json_val:
                        try:
                            print("saving db")
                            # time.sleep(5)
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
                                    print("filetype is", FileType)
                                    if not FileDataToBeStored.objects.filter(NodeId=NodeId, FileId=FileId).exists():
                                        file_in_db = FileDataToBeStored.objects.create(appavailableindb=app_in_db,
                                                                                        FileId=FileId, NodeId=NodeId,
                                                                                        FileType=FileType, FileUrl=FileUrl,
                                                                                        DateUpdated=DateUpdated, 
                                                                                        fileName=fileName)
                                        file_in_db.save()

                        except requests.exceptions.ConnectionError:
                            print("db error")
                            return HttpResponseRedirect('/channel/no_internet/')

            except requests.exceptions.ConnectionError:
                print("downlaod error ")
                return HttpResponseRedirect('/channel/no_internet/')

        # return HttpResponse("success!!")
        print("successfully saved!")
        return HttpResponse("success")


class NoInternetView(TemplateView):
    template_name = 'channels/no_internet.html'

