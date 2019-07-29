from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from casino.forms import RegistrationForm
from casino.models import Wallet


def index(request):
    real_money: float = 0.0
    bonus_money: float = 0.0
    if request.user.is_authenticated:
        wallet = Wallet.objects.get(customeruser=request.user)
        real_money = wallet.real_money
        bonus_money = wallet.bonus_money
    return render(
        request,
        'index.html',
        {
            'real': real_money,
            'bonus': bonus_money,
        }
    )


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
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
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


def login_user(request):
    if request.method == 'POST':
        username: str = request.POST.get('username')
        password: str = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request=request, user=user)

            # updates wallet for every login
            wallet = Wallet.objects.get(customeruser=user)
            wallet.give_login_bonus()
            return HttpResponseRedirect(reverse('index'))
        else:
            # log stuff here
            return HttpResponse('You have provided wrong credentials')
    else:
        return render(request, 'login.html', {})


@login_required
def deposit(request):
    deposited = False
    amount = 0.0
    wallet: Wallet = None
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            wallet = Wallet.objects.get(customeruser=request.user)
            wallet.deposit_amount(amount)

            deposited = True
        except ValueError:
            return redirect('index')

    return render(
        request,
        'index.html',
        {
            'deposited': deposited,
            'amount': abs(amount),
            'real': wallet.real_money,
            'bonus': wallet.bonus_money,
        }
    )


@login_required
def spin(request):
    spin_amount: float = 2.0
    win, lose, choice = 0., 0., ''
    spined: bool = False
    wallet = None
    if request.method == 'POST':
        try:
            spin_amount = float(request.POST.get('spin_amount'))
        except ValueError:
            print(f'Using sping amount of {spin_amount} euros')

        wallet = Wallet.objects.get(customeruser=request.user)
        win, lose, choice = wallet.spin(abs(spin_amount))
        spined = True

    return render(
        request,
        'index.html',
        {
            'real': wallet.real_money,
            'bonus': wallet.bonus_money,
            'value': win if choice == 'won' else lose,
            'choice': choice,
            'spined': spined
        }
    )
