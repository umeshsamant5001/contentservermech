from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from pprint import pprint
from django.conf import settings
from django.contrib.sessions.models import Session
from pathlib import Path
from django.db.models import F
from django.contrib.auth.models import User
from .models import VillageDataStore
from channels.models import AppAvailableInDB, AppListFromServerData, FileDataToBeStored
import requests
import string
import random
import json


homeDir = str(Path.home())

headers = {
    'cache-control': "no-cache",
    'content-type': "application/json",
    "Accept": "application/json"
}


def check_internet(request):
    return render(request, 'core/NoInternetFound.html')


def home(request):
    try:
        applistindb = AppListFromServerData.objects.all()
        appindb = AppAvailableInDB.objects.all()
        filedataindb = FileDataToBeStored.objects.all()
        user_data = User.objects.all()

        n = 12
        randstr_session = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

        if not user_data and not appindb and not applistindb and not filedataindb:
            # fetching programs from server
            programs_urls = "http://swap.prathamcms.org/api/program"
            program_api_response = requests.request(
                'get', programs_urls, headers=headers)
            program_api_result = json.loads(
                program_api_response.content.decode("utf-8"))
            context = {
                'program_result': program_api_result
            }
            request.session['session_id'] = randstr_session
            print(request.session.get('session_id', randstr_session))
            return render(request, 'setup_index.html', context)
        else:
            request.session['session_id'] = randstr_session
            print(request.session.get('session_id', randstr_session))
            return HttpResponseRedirect(reverse('content_viewer:app_available'))
    except Exception as e:
        print("setup error is:---", e)
        return check_internet(request)


@login_required
def program_call(request):
    try:
        program_url = "http://swap.prathamcms.org/api/program"
        program_response = requests.get(program_url, headers=headers)
        program_result = json.loads(program_response.content.decode('utf-8'))
        context = {
            'program_result': program_result,
        }
        return render(request, 'core/index.html', context)
    except Exception as e:
        print("program error is:---", e)
        return check_internet(request)


def state_call(request):
    global program_id, state_result
    try:
        program_id = ''
        if request.method == 'GET':
            program_id = request.GET.get('program_id')
        state_url = "http://swap.prathamcms.org/api/state?progid=%s" % (
            program_id)
        state_response = requests.get(state_url, headers=headers)
        state_result = json.loads(state_response.content.decode('utf-8'))
        context = {
            "states": state_result,
        }
        return render(request, 'core/states.html', context)
    except Exception as e1:
        print("state error is:---", e1)
        return check_internet(request)


# function to fetch district
def district_call(request):
    # fetching stateId from template and serving to urls
    global state_id, dist_list, dist_api_result
    state_id = ''
    if request.method == 'GET':
        state_id = request.GET.get('state_id')

    # getting data from server for district
    dist_url = "http://www.hlearning.openiscool.org/api/village/get?programid=%s&state=%s" % (
        program_id, state_id)
    dist_api_response = requests.request('get', dist_url, headers=headers)
    dist_api_result = json.loads(dist_api_response.content.decode('utf-8'))

    # all_villages = dist_api_result
    dist_list = []
    for dist in dist_api_result:
        dist = dist['District']
        dist_list.append(dist)

    unique_dist = set(dist_list)

    context = {
        'districts': unique_dist
    }

    return render(request, 'core/district.html', context)


# fetching block data
def block_call(request):
    # accessing block value from template
    global block_list, district_name
    block_list = set()
    district_name = ''
    if request.method == 'GET':
        district_name = request.GET.get('district_name')
        for block in dist_api_result:
            if district_name == block['District']:
                block_list.add(block['Block'])

    ordered_block_list = set(block_list)  # filtering block list uniquely
    context = {
        'blocks': ordered_block_list
    }

    return render(request, 'core/blocks.html', context)


# getting village list on basis of program, state, district, block
def show_villages(request):
    global village_list, block_name
    block_name = ''

    # list for selected villages
    village_list = []

    if request.method == 'GET':
        block_name = request.GET.get('block_name')
        for selected in dist_api_result:
            if block_name == selected['Block']:
                village_list.append(selected)

    context = {
        'villages': village_list
    }

    return render(request, 'core/villages.html', context)


# post crl, village, student and group data according to villages
def post_all_data(request):
    global village_ids
    # village_ids = None
    if request.method == 'POST':
        village_ids = request.POST.getlist('village_values[]')

    # list of villages to be posted
    villages_to_post = []

    for ids in village_ids:
        for villages in village_list:
            if str(ids) == str(villages['VillageId']):
                villages_to_post.append(villages)
            else:
                continue

    # crl data fetching and saving
    crl_url = "http://www.hlearning.openiscool.org/api/crl/get/?programid=%s&state=%s" % (
        program_id, state_id)
    crl_response = requests.get(crl_url, headers=headers)
    crl_result = json.loads(crl_response.content.decode('utf-8'))

    # saving crls data into db and delete duplicate content
    try:
        # crl filter
        crl_filter = "programid:" + program_id + ",state:" + state_id
        crl_table_data = VillageDataStore.objects.filter(
            filter_name=crl_filter, table_name="crl", key_id=crl_filter)

        for datas in crl_table_data:
            if datas.filter_name and datas.table_name and datas.key_id:
                datas.delete()
            else:
                continue
        crl_data = VillageDataStore.objects.create(data=crl_result, filter_name=crl_filter,
                                                   table_name="crl", key_id=crl_filter)
        crl_data.save()
    except requests.exceptions.ConnectionError as crl_error:
        print("crl error ---", crl_error)

    # posting the state data where key id will be AutoId
    try:
        state_key_id = ''
        state_data_to_post = ''
        for st in state_result:
            if st['StateCode'] == state_id:
                state_key_id = st['AutoId']
                state_data_to_post = st

        state_filter = "programid:" + program_id + ",state:" + state_id
        state_table_data = VillageDataStore.objects.filter(filter_name=state_filter,
                                                           table_name="state", key_id=state_key_id)

        for datas in state_table_data:
            if datas.filter_name and datas.table_name and datas.key_id:
                datas.delete()
            else:
                continue

        state_data = VillageDataStore.objects.create(data=state_data_to_post, 
                                                     filter_name=state_filter,
                                                     table_name="state", key_id=state_key_id)
        state_data.save()

    except requests.exceptions.ConnectionError as state_error:
        print("state error is ", state_error)

    # saving selected village data into db
    for villages in villages_to_post:
        try:
            village_filter = "programid:" + program_id + ",state:" + state_id
            village_table_data = VillageDataStore.objects.filter(filter_name=village_filter,
                                                                 table_name='village', key_id=str(villages['VillageId']))
            # print(villages, "something")
            for datas in village_table_data:
                if datas.filter_name and datas.table_name and datas.key_id:
                    print("deleting")
                    datas.delete()
                    print("deleted")
                else:
                    continue

            # saving village data in db
            village_data_to_post = VillageDataStore.objects.create(data=villages, filter_name=village_filter,
                                                                   table_name="village", key_id=str(villages['VillageId']))
            village_data_to_post.save()
        except Exception as village_error:
            print("village error ---", village_error)

        try:
            grp_std_ids = str(villages['VillageId'])

            grp_url = "http://www.devtab.openiscool.org/api/Group/?programid=%s&villageId=%s" % (
                program_id, grp_std_ids)
            grp_response = requests.get(grp_url, headers=headers)
            grp_result = json.loads(grp_response.content.decode("utf-8"))

            # group and student data filter column
            grp_std_filter = "programid:" + program_id + \
                ",villageid:" + str(grp_std_ids)

            # filtering group data table
            grp_table_data = VillageDataStore.objects.filter(
                filter_name=grp_std_filter, table_name="group", key_id=grp_std_ids)

            # deleting group data on basis of filter_name, table_name and key_id
            for grps in grp_table_data:
                print(grps.filter_name, grps.table_name, grps.key_id, "gpn")
                if grps.filter_name and grps.table_name and grps.key_id:
                    grps.delete()
                else:
                    continue

            # saving data of groups in db
            group_data = VillageDataStore.objects.create(data=grp_result, filter_name=grp_std_filter,
                                                         table_name="group", key_id=grp_std_ids)
            group_data.save()
        except Exception as grp_error:
            print("grp error ---", grp_error)

        try:
            # student data fetching, filtering and saving
            std_url = "http://www.devtab.openiscool.org/api/student/?programid=%s&villageId=%s" % (
                program_id, grp_std_ids)
            std_response = requests.get(std_url, headers=headers)
            std_result = json.loads(std_response.content.decode("utf-8"))

            # filtering student data table
            std_table_data = VillageDataStore.objects.filter(filter_name=grp_std_filter,
                                                             table_name="student", key_id=grp_std_ids)

            # delting student data from table
            for stds in std_table_data:
                print(stds.filter_name, stds.table_name, stds.key_id, "stdb")
                if stds.filter_name and stds.table_name and stds.key_id:
                    stds.delete()
                else:
                    continue

            # saving student data in table
            student_data = VillageDataStore.objects.create(data=std_result, filter_name=grp_std_filter,
                                                           table_name="student", key_id=grp_std_ids)
            student_data.save()
        except Exception as std_error:
            print("std error ---", std_error)

    return HttpResponse("success")


def user_register(request):
    users_list = []
    user_url = "http://www.hlearning.openiscool.org/api/crl/get/?programid=%s&state=%s" % (
        program_id, state_id)
    user_response = requests.get(user_url, headers=headers)
    user_result = json.loads(user_response.content.decode('utf-8'))

    # fetching all users from table
    all_users = User.objects.all()

    for i in user_result:
        username = i['UserName']
        password = i['Password']
        email = i['Email']
        first_name = i['FirstName']
        last_name = i['LastName']

        # checking if User table is empty or not
        if all_users:
            # filtering if table is not empty according to username
            present_users = User.objects.filter(username=i['UserName'])
            # deleting specific column according to username
            for j in present_users:
                j.delete()
        else:
            pass

        # creating and saving user in user table(auth_user)
        # user = User.objects.create_user(username=username, password=password,
        #                                 email=email, first_name=first_name, last_name=last_name)
        # user.save()
        users_list.append(User(username=username, password=make_password(password),
                               email=email, first_name=first_name, last_name=last_name))

    # print('user list is ', users_list)

    User.objects.bulk_create(users_list, ignore_conflicts=True)

    return HttpResponse("success")
