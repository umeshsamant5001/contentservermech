from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserAuthenticationForm



@login_required
def user_logout(request):
    logout(request)
    return redirect('core:home')


def user_login(request):
    context = {}
    user = request.user

    if user.is_authenticated:
        return redirect('content_viewer:app_available')

    if request.POST:
        form = UserAuthenticationForm(request.POST)

        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user:
                login(request,user)
                return redirect('content_viewer:app_available')
    else:
        form = UserAuthenticationForm()

    context['login_form'] = form
    return render(request, 'account/login.html', context)


