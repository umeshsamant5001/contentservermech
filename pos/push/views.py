from django.shortcuts import render
from django.http import HttpResponse
from channels.models import (AppListFromServerData, AppAvailableInDB,
                             FileDataToBeStored, FileUpload)
from core.models import UsageData


def push_data(request):
    from django.db import connection
    usage = UsageData.objects.raw("select id, data, filter_name from core_usagedata")
    for u in usage:
        print(u.filter_name)
    return HttpResponse("this is push view")


