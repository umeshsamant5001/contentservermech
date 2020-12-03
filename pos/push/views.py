import os
import json
import string
import random
import platform
import datetime
import requests
import time
from pathlib import Path
from django.contrib import messages
from core.models import UsageData, DeskTopData
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.sessions.models import Session


system_os = platform.system()
print(system_os)

headers = {
    'cache-control': "no-cache",
    'content-type': "application/json",
    'Accept': 'application/json'
}


def push_data(request):
    return render(request, 'push/data_to_push.html')


def create_usage_directory():
    # global homeDir
    if system_os == "Windows":
        homeDir = str(Path.home())
        homeDir = os.path.join(homeDir, r"generate\Backup")
        usageDir = os.path.join(homeDir, "usageData")
        if not os.path.exists(usageDir):
            os.makedirs(usageDir)
        else:
            pass
    else:
        homeDir = str(Path.home())
        homeDir = os.path.join(homeDir, "generate/Backup")
        usageDir = os.path.join(homeDir, "usageData")
        if not os.path.exists(usageDir):
            os.makedirs(usageDir)
        else:
            pass

    # print("homeDir is from create_dir ", homeDir)
    return usageDir


def create_desktop_directory():
    # global homeDir
    if system_os == "Windows":
        homeDir = str(Path.home())
        homeDir = os.path.join(homeDir, r"generate\Backup")
        desktopDir = os.path.join(homeDir, "desktopData")
        if not os.path.exists(desktopDir):
            os.makedirs(desktopDir)
        else:
            pass
    else:
        homeDir = str(Path.home())
        homeDir = os.path.join(homeDir, "generate/Backup")
        desktopDir = os.path.join(homeDir, "desktopData")
        if not os.path.exists(desktopDir):
            os.makedirs(desktopDir)
        else:
            pass

    # print("homeDir is from create_dir ", homeDir)
    return desktopDir


def push_usageData(request):
    i = 1
    n = 6
    serial_line = ''
    randstr = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(n))

    while True:
        fetch_url = "http://localhost:8000/api/usagedata/?table_name=USAGEDATA&page=%s&page_size=15" % i

        # post api
        post_url = "http://rpi.prathamskills.org/api/KolibriSession/Post"

        response = requests.get(fetch_url)

        lstscore = json.loads(response.content.decode('utf-8'))
        print("lstscore ", lstscore['count'])

        # pi id data to be collected
        os.system('cat /proc/cpuinfo > serial_data.txt')
        serial_file = open('serial_data.txt', "r+")
        for line in serial_file:
            if line.startswith('Serial'):
                serial_line = line

        lstscore['serial_id'] = serial_line

        # checks the value of count
        if lstscore['count'] == 0 and lstscore['next'] is None:
            print("no data")
            return render(request, 'push/data_to_push.html')
        elif lstscore['count'] != 0 and lstscore['next'] is None:
            try:
                data = lstscore
                response_post = requests.post(
                    post_url,
                    headers=headers,
                    data=json.dumps(data),
                )

                # print("elif", response_post.status_code, response_post.reason)
            except Exception as bkp_error_next:
                print("bkp error is ", bkp_error_next)
            return render(request, 'push/data_to_push.html')
        else:
            data = lstscore  # providing lstscore value to data variable
            try:
                response_post = requests.post(
                    post_url,
                    headers=headers,
                    data=json.dumps(data),
                )

                # print("el", response_post.status_code, response_post.reason)

            except Exception as e1:
                print("error e1 is ", e1)
                return False
        i = i+1
    return render(request, 'push/data_to_push.html')


def backup(request):
    i = 1
    n = 6
    serial_line = ''
    randstr = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(n))

    while True:
        # usagedata backup code
        # get api
        usage_url = "http://localhost:8000/api/usagedata/?table_name=USAGEDATA&page=%s&page_size=15" % i
        print("usage_url ", usage_url)

        response = requests.get(usage_url)

        lstscore = json.loads(response.content.decode('utf-8'))

        print(response.status_code)
        if response.status_code == 404:
            return render(request, 'push/data_to_push.html')

        # pi id data to be collected
        os.system('cat /proc/cpuinfo > serial_data.txt')
        serial_file = open('serial_data.txt', "r+")
        for line in serial_file:
            if line.startswith('Serial'):
                serial_line = line

        lstscore['serial_id'] = serial_line

        if lstscore['count'] == 0 and lstscore['next'] is None:
            print("no data")
            return render(request, 'push/data_to_push.html')
        elif lstscore['count'] != 0 and lstscore['next'] is None:
            try:
                with open(os.path.join(create_usage_directory(),
                                       randstr + str(datetime.datetime.now()) + '.json'),
                          "w") as outfile:
                    json.dump(lstscore, outfile, indent=4, sort_keys=True)
            except Exception as bkp_error_next:
                print("bkp error is ", bkp_error_next)
                return render(request, 'push/data_to_push.html')
        else:
            print("lstscore ", lstscore['next'])
            try:
                with open(os.path.join(create_usage_directory(),
                                       randstr + str(datetime.datetime.now()) + '.json'),
                          "w") as outfile:
                    json.dump(lstscore, outfile, indent=4, sort_keys=True)
            except Exception as bkp_error:
                print("bkp error is ", bkp_error)
                return render(request, 'push/data_to_push.html')

        # desktop data backup
        desktop_url = "http://localhost:8000/api/desktopdata/?page=%s&page_size=15" % i
        appList_url = "http://localhost:8000/api/channel/AppList/"

        # desktop data url
        desktop_response = requests.get(desktop_url, headers=headers)
        desktop_result = json.loads(desktop_response.content.decode('utf-8'))

        # app list url
        appList_response = requests.get(appList_url, headers=headers)
        appList_result = json.loads(appList_response.content.decode('utf-8'))

        if desktop_response.status_code == 404 and appList_response.status_code == 404:
            return render(request, 'push/data_to_push.html')
        elif desktop_response.status_code == 404:
            return render(request, 'push/data_to_push.html')
        else:
            pass

        if desktop_result['count'] == 0 and desktop_result['next'] is None:
            # print("no data")
            return render(request, 'push/data_to_push.html')
        elif desktop_result['count'] != 0 and desktop_result['next'] is None:
            try:
                desktop_data_to_post = {
                    "desktop_result": desktop_result,
                    "appList_result": appList_result,
                }
                try:
                    with open(os.path.join(create_desktop_directory(),
                                        randstr + str(datetime.datetime.now()) + '.json'),
                            "w") as outfile:
                        json.dump(desktop_data_to_post, outfile, indent=4, sort_keys=True)
                except Exception as bkp_error_next:
                    print("bkp error is ", bkp_error_next)
                    return render(request, 'push/data_to_push.html')

            except Exception as e:
                # return False
                return render(request, 'push/data_to_push.html')
        else:
            try:
                desktop_data_to_post = {
                    "desktop_result": desktop_result,
                    "appList_result": appList_result,
                }
                try:
                    with open(os.path.join(create_desktop_directory(),
                                        randstr + str(datetime.datetime.now()) + '.json'),
                            "w") as outfile:
                        json.dump(desktop_data_to_post, outfile, indent=4, sort_keys=True)
                except Exception as bkp_error_next:
                    print("bkp error is ", bkp_error_next)
                    return render(request, 'push/data_to_push.html')

            except Exception as e:
                print("dtp post error ", e)
                return False
            # return render(request, 'push/data_to_push.html')


        i = i+1

    return render(request, 'push/data_to_push.html')


def clear_data(request):
    instance_usage = UsageData.objects.all()
    instance_usage.delete()
    instance_desktop = DeskTopData.objects.all()
    instance_desktop.delete()
    return render(request, 'push/data_to_push.html')


def desktop_data_to_server(request):
    i = 1
    n = 6
    serial_line = ''
    randstr = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(n))

    if request.session.has_key('session_id'):
        sessionId = request.session.get('session_id')

    while True:
        # get api
        desktop_url = "http://localhost:8000/api/desktopdata/?page=%s&page_size=15" % i
        appList_url = "http://localhost:8000/api/channel/AppList/"

        # post api
        post_url = "http://rpi.prathamskills.org/api/KolibriSession/Post"

        # desktop data url
        desktop_response = requests.get(desktop_url, headers=headers)
        desktop_result = json.loads(desktop_response.content.decode('utf-8'))

        # app list url
        appList_response = requests.get(appList_url, headers=headers)
        appList_result = json.loads(appList_response.content.decode('utf-8'))

        if desktop_response.status_code == 404 and appList_response.status_code == 404:
            return render(request, 'push/data_to_push.html')
        elif desktop_response.status_code == 404:
            return render(request, 'push/data_to_push.html')
        else:
            pass

        if desktop_result['count'] == 0 and desktop_result['next'] is None:
            # print("no data")
            return render(request, 'push/data_to_push.html')
        elif desktop_result['count'] != 0 and desktop_result['next'] is None:
            try:
                desktop_data_to_post = {
                    "desktop_result": desktop_result,
                    "appList_result": appList_result,
                }
                response_post = requests.post(
                    post_url,
                    headers=headers,
                    data=json.dumps(desktop_data_to_post),
                )
                print(response_post.status_code, response_post.reason)
                # from pprint import pprint
                # pprint(desktop_data_to_post)

            except Exception as e:
                # return False
                return render(request, 'push/data_to_push.html')
        else:
            try:
                desktop_data_to_post = {
                    "desktop_result": desktop_result,
                    "appList_result": appList_result,
                }
                response_post = requests.post(
                    post_url,
                    headers=headers,
                    data=json.dumps(desktop_data_to_post),
                )
                print(response_post.status_code, response_post.reason)
                # from pprint import pprint
                # pprint(desktop_data_to_post)

            except Exception as e:
                print("dtp post error ", e)
                return False
            # return render(request, 'push/data_to_push.html')

        i = i+1

    return render(request, 'push/data_to_push.html')
