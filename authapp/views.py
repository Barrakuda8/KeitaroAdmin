from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from authapp.forms import UserLoginForm


def index(request):
    if request.user.is_authenticated:
        if request.user.support_id:
            return HttpResponseRedirect(reverse('adminapp:accounts'))
        else:
            return HttpResponseRedirect(reverse('adminapp:stats'))
    else:
        return HttpResponseRedirect(reverse('authapp:login'))


def login(request):
    login_form = UserLoginForm(data=request.POST)
    if request.method == 'POST' and login_form.is_valid():
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user and not user.is_deleted:
            auth.login(request, user)
            if request.user.support_id:
                return HttpResponseRedirect(reverse('adminapp:accounts'))
            else:
                return HttpResponseRedirect(reverse('adminapp:stats'))

    context = {
        'title': 'Авторизация',
        'login_form': login_form,
    }

    return render(request, 'authapp/login.html', context=context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('authapp:login'))
