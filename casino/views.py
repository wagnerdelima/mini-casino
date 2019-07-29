from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from casino.forms import RegistrationForm
from casino.models import Wallet, Bonus, CustomerUser


def sum_bonuses(user_id):
    bonus_money = 0.0
    bonuses = Bonus.objects.filter(
        customer_id=user_id,
        is_bonus_depleted=False
    ).order_by('-wagering_requirement')

    for bonus in bonuses:
        bonus_money += bonus.bonus_money

    return bonus_money, bonuses[0]


def index(request):
    real_money: float = 0.0
    bonus_money: float = 0.0
    wagering = 0.0
    if request.user.is_authenticated:
        wallet = Wallet.objects.get(customer_id=request.user.id)

        bonus_money, bonus = sum_bonuses(request.user.id)
        wagering = bonus.wagering_requirement
        real_money = wallet.real_money
    return render(
        request,
        'index.html',
        {
            'real': real_money,
            'bonus': bonus_money,
            'wager': wagering
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

            user = CustomerUser.objects.get(id=user.id)
            Wallet(customer=user).save()
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
            user = CustomerUser.objects.get(id=user.id)
            bonus = Bonus(customer=user)
            bonus.give_login_bonus()
            bonus.save()
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
    real: float = 0.0
    bonus: float = 0.0
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            wallet = Wallet.objects.get(customer_id=request.user.id)
            real = wallet.deposit_amount(amount)
            bonus = sum_bonuses(request.user.id)

            deposited = True
        except ValueError:
            return redirect('index')

    return render(
        request,
        'index.html',
        {
            'deposited': deposited,
            'amount': abs(amount),
            'real': real,
            'bonus': bonus,
        }
    )


@login_required
def spin(request):
    if request.method == 'POST':
        wallet = Wallet.objects.get(customer_id=request.user.id)
        win, lose, choice = wallet.spin()
        bonus_money, wager = sum_bonuses(request.user.id)
        bonus_wagered_to_wallet = wager.automatic_wagering(
            wallet.amount_lost
        )
        wallet.grant_wagered(bonus_wagered_to_wallet)
        spined = True

        return render(
            request,
            'index.html',
            {
                'real': wallet.real_money,
                'bonus': bonus_money,
                'wager': wager.wagering_requirement,
                'value': win if choice == 'won' else lose,
                'choice': choice,
                'spined': spined
            }
        )
    return redirect('index')
