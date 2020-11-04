import os, time
import platform
from pathlib import Path
from itertools import chain
from django.http import HttpResponse
from content_viewer.extracter import extraction
from content_viewer.converter import m4v_to_mp4, wav_to_mp3
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from channels.models import AppListFromServerData, AppAvailableInDB, FileDataToBeStored


system_os = platform.system()

# checking the list of available apps
class AppAvailableListView(LoginRequiredMixin, ListView):
    model = AppListFromServerData
    template_name = "content_viewer/app_available.html"

    def get_queryset(self, *args, **kwargs):
        queryset = AppListFromServerData.objects.all()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(AppAvailableListView, self).get_context_data(*args, **kwargs)
        queryset = self.get_queryset()
        context["apps_list"] = queryset
        # print("context is ", context)
        return context


class ParentAppView(LoginRequiredMixin, ListView):
    # model = AppAvailableInDB
    template_name = "content_viewer/app_details.html"

    def get_queryset(self, *args, **kwargs):
        AppId = self.kwargs['AppId']
        queryset = FileDataToBeStored.objects.all().select_related('appavailableindb').filter(appavailableindb__AppId=AppId)
        return queryset

    def get_context_data(self, *args, **kwargs):
        # print("AppId is ", AppId)
        context = super(ParentAppView, self).get_context_data(*args, **kwargs)
        queryset = self.get_queryset()
        app_name = ''
        context["parent_details"] = queryset
        return context


class ChildrenAppView(LoginRequiredMixin, ListView):
    template_name = "content_viewer/child_details.html"

    def get_queryset(self, *args, **kwargs):
        global NodeId
        NodeId = self.kwargs['NodeId']
        print("child NodeId is ", NodeId)
        queryset = FileDataToBeStored.objects.all().prefetch_related('appavailableindb').filter(appavailableindb__ParentId=NodeId)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(ChildrenAppView, self).get_context_data(*args, **kwargs)
        queryset = self.get_queryset()
        app_name = AppListFromServerData.objects.all()
        parent_db = AppAvailableInDB.objects.filter(NodeId=NodeId)
        parent_db_title = AppAvailableInDB.objects.filter(NodeId=NodeId)
        print("prdfb is", parent_db_title)
        for title in parent_db_title:
            print("parent_db_title", title.NodeTitle)
        combined_results = ''
        chaining_queries = []
    
        while parent_db:
            parent_id = parent_db.first().ParentId
            parent_db = AppAvailableInDB.objects.filter(NodeId=parent_id)
            if not parent_db:
                # print("prdb is ", parent_db)
                pass
            else:
                parent_db = AppAvailableInDB.objects.filter(NodeId=parent_id)
                chaining_queries.append(parent_db)
        combined_results = list(chain(chaining_queries[::-1]))
        context['chaining_queries'] = combined_results
        context['app_name'] = app_name
        context['child_details'] = queryset
        # print(context)
        context['parent_db_title'] = parent_db_title
        return context


def resource_view(request, NodeId):
    context = {}
    queryset = FileDataToBeStored.objects.filter(NodeId=NodeId)
    zip_path = os.getcwd()
    general_path = os.getcwd()
    app_name = AppListFromServerData.objects.all()
    parent_db = AppAvailableInDB.objects.filter(NodeId=NodeId)
    combined_results = ''
    chaining_queries = []
        
    while parent_db:
        parent_id = parent_db.first().ParentId
        parent_db = AppAvailableInDB.objects.filter(NodeId=parent_id)
        if not parent_db:
            pass
        else:
            parent_db = AppAvailableInDB.objects.filter(NodeId=parent_id)
            chaining_queries.append(parent_db)
    
    combined_results = list(chain(chaining_queries[::-1]))
    context['chaining_queries'] = combined_results
    context['app_name'] = app_name
    # print("genral path is ", general_path, zip_path)
    if system_os == "Windows":
        zip_path = os.path.join(zip_path, r'storage\content\zips')
        vid_m4v_path = os.path.join(general_path, r'storage\content\videos\m4v')
        audio_wav_path = os.path.join(general_path, r'storage\content\videos\wav')
    else:
        zip_path = os.path.join(zip_path, 'storage/content/zips')
        vid_m4v_path = os.path.join(general_path, 'storage/content/videos/m4v')
        # print("vid_m4v_path path is ", vid_m4v_path, zip_path)
        audio_wav_path = os.path.join(general_path, 'storage/content/audios/wav')
        # print("audio_wav_path path is ", audio_wav_path, zip_path)
    for qs in queryset:
        if qs.FileType == "Content" and qs.fileName.endswith('.zip'):
            zip_path1 = os.path.join(zip_path, qs.fileName)
            qs.fileName = extraction(zip_path1)
            zip_path = os.path.join(zip_path, qs.fileName)
            context['file'] = qs.fileName
            context['game_play'] = queryset
            return render(request, "content_viewer/content_play.html", context=context)
        elif qs.FileType == "Content" and qs.fileName.endswith('.mp4'):
            context['video_play'] = queryset
            # print(context)
            return render(request, "content_viewer/content_play.html", context=context)
        elif qs.FileType == "Content" and qs.fileName.endswith('.m4v'):
            vid_m4v_path1 = os.path.join(vid_m4v_path, qs.fileName)
            # print("vid_m4v_path1!!!", vid_m4v_path1, vid_m4v_path, qs.fileName)
            qs.fileName = m4v_to_mp4(vid_m4v_path1)
            # print("qs.fileName!!!", qs.fileName)
            print("converted!!!")
            # time.sleep(50)
            context['video_play'] = queryset
            print(context)
            return render(request, "content_viewer/content_play.html", context=context)
        elif qs.FileType == "Content" and qs.fileName.endswith('.mp3'):
            context['audio_play'] = queryset
            return render(request, "content_viewer/content_play.html", context=context)
        elif qs.FileType == "Content" and qs.fileName.endswith('.wav'):
            audio_wav_path1 = os.path.join(audio_wav_path, qs.fileName)
            qs.fileName = wav_to_mp3(audio_wav_path1)
            print("audio converted!!!")
            context['audio_play'] = queryset
            return render(request, "content_viewer/content_play.html", context=context)
        elif qs.FileType == "Content" and qs.fileName.endswith('.png' or '.jpg' or '.jpeg' or '.mpeg'):
            context['wrong_format'] = queryset
            return render(request, "content_viewer/content_play.html", context=context)
        elif qs.FileType == "Content" and qs.fileName.endswith('.pdf'):
            context['pdf_play'] = queryset
            return render(request, "content_viewer/content_play.html", context=context)


    