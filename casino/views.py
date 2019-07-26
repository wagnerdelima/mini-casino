from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from casino.forms import RegistrationForm, LoginForm


def index(request):
    return render(request, 'index.html')


@login_required
def special(request):
    return HttpResponse("You have just logged in!")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    is_registered: bool = False
    if request.method == 'POST':
        user_form = RegistrationForm(data=request.POST)
        if user_form.is_valid():
            user_form.save(commit=True)
            is_registered = True
        else:
            print(user_form.errors)
    else:
        user_form = RegistrationForm()
    return render(
        request,
        'registration.html',
        {
            'user_form': user_form,
            'registered': is_registered
        }
    )


def login(request):
    if request.method == 'POST':
        username: str = request.POST.get('username')
        password: str = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            # log stuff here
            return HttpResponse('You have provided wrong credentials')
    else:
        return render(request, 'login.html', {})
