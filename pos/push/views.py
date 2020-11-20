import os
import json
import string
import random
import platform
import datetime
import requests
from pathlib import Path
from django.contrib import messages
from core.models import UsageData
from django.shortcuts import render
from django.http import HttpResponse

system_os = platform.system()
print(system_os)

headers = {
    'cache-control': "no-cache",
    'content-type': "application/json",
    'Accept': 'application/json'
}

def push_data(request):
    return render(request, 'push/data_to_push.html')

def create_directory():
    # global homeDir
    if system_os == "Windows":
        homeDir = str(Path.home())
        homeDir = os.path.join(homeDir, r"generate\Backup")
        if not os.path.exists(homeDir):
            os.makedirs(homeDir)

        else:
            pass
    else:
        homeDir = str(Path.home())
        homeDir = os.path.join(homeDir, "generate/Backup")
        if not os.path.exists(homeDir):
            os.makedirs(homeDir)
        else:
            pass
    
    print("homeDir is from create_dir ", homeDir)
    return homeDir

def push_usageData(request):
    i = 1
    n = 6
    serial_line = ''
    randstr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
    
    while True:
        fetch_url = "http://localhost:8000/api/usagedata/?table_name=USAGEDATA&page=%s&page_size=15" % i
        print("url is ", fetch_url)

        #post api
        post_url = "http://www.rpi.prathamskills.org/api/pushdata/post/"

        response = requests.get(fetch_url)

        lstscore = json.loads(response.content.decode('utf-8'))
        print("lstscore ", lstscore['count'])

        # pi id data to be collected
        # os.system('cat /proc/cpuinfo > serial_data.txt')
        # serial_file = open('serial_data.txt', "r+")
        # for line in serial_file:
        #     if line.startswith('Serial'):
        #         serial_line = line
        #
        # lstscore['serial_id'] = serial_line

        # checks the value of count
        if lstscore['count'] == 0:
            return render(request, 'push/data_to_push.html')
        
        else:
            headers = {
                "content-type": "application/json"
            }
            data = lstscore  # providing lstscore value to data variable

            try:
                response_post = requests.post(
                    post_url,
                    headers=headers,
                    data=json.dumps(data),
                )

                print(response_post.status_code, response_post.reason)
            
                if response.status_code == 200:
                    for obj in lstscore['results']:
                        show_id = obj['id']
                        url_del = "http://localhost:8000/api/usagedata/" + str(show_id)
                        try:
                            res_del = requests.delete(url_del, headers=headers)
                        except Exception as e:
                            print("error e is ", e)
                            return False
                    try:
                        with open(os.path.join(create_directory(), randstr + str(datetime.datetime.now()) + '.json'),
                                      "w") as outfile:
                                json.dump(lstscore, outfile, indent=4, sort_keys=True)
                    except Exception as err:
                        print("cannot create backup due to ", err)
                else:
                    return False

            except Exception as e1:
                print("error e1 is ", e1)
                return False

    return render(request, 'push/data_to_push.html')


def backup(request):
    i = 1
    n = 6
    serial_line = ''
    randstr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

    while True:
        #get api
        usage_url = "http://localhost:8000/api/usagedata/?table_name=USAGEDATA&page=%s&page_size=15" % i
        #post api
        # post_url = "http://www.rpi.prathamskills.org/api/pushdata/post/"

        response = requests.get(usage_url)

        lstscore = json.loads(response.content.decode('utf-8'))

        if lstscore['count'] == 0 and lstscore['next'] is None:
            print("no data")
            return render(request, 'push/data_to_push.html')
        elif lstscore['count'] != 0 and lstscore['next'] is None:
            try:
                with open(os.path.join(create_directory(),
                                                   randstr + str(datetime.datetime.now()) + '.json'),
                                      "w") as outfile:
                                json.dump(lstscore, outfile, indent=4, sort_keys=True)
            except Exception as bkp_error_next:
                print("bkp error is ", bkp_error_next)
            return render(request, 'push/data_to_push.html')
        else:
            print("lstscore ", lstscore['next'])
            import time
            time.sleep(3)
            try:
                with open(os.path.join(create_directory(),
                                                   randstr + str(datetime.datetime.now()) + '.json'),
                                      "w") as outfile:
                                json.dump(lstscore, outfile, indent=4, sort_keys=True)
            except Exception as bkp_error:
                print("bkp error is ", bkp_error)

        i=i+1


    return render(request, 'push/data_to_push.html')


def clear_data(request):
    instance = UsageData.objects.all()
    instance.delete()
    return render(request, 'push/data_to_push.html')

