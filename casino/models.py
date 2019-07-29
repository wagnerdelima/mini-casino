import random
from typing import Tuple

from django.db import models
from django.db import transaction, IntegrityError

from django.contrib.auth.models import User


class Bonus(models.Model):
    customer = models.ForeignKey(
        'CustomerUser',
        blank=False,
        null=True,
        on_delete=models.CASCADE
    )

    bonus_money = models.FloatField(
        blank=False,
        null=False,
        default=0.0,
        help_text='Customer bonus amount'
    )

    wagered = models.FloatField(
        blank=False,
        null=False,
        default=0.0,
        help_text='Wagered amount that can be withdrawn'
    )

    wagering_requirement = models.FloatField(
        blank=False,
        null=False,
        default=0.0,
        help_text='Wagering requirement'
    )

    casino_bonus_login = models.FloatField(
        blank=False,
        null=False,
        default=100.0,
        help_text='Customer bonus amount'
                  ' given by log ins'
    )

    is_bonus_depleted = models.BooleanField(
        default=False
    )

    def wagering(self):
        cashing: int = random.randint(1, 20) * self.bonus_money
        self.wagering_requirement = cashing

    def is_wallet_depleted(self):
        """
        Checks if bonus is 0 and
        therefore depleted
        :return: Bool
        """
        return self.bonus_money == 0

    def deplete_bonus(self):
        try:
            with transaction.atomic():
                self.is_bonus_depleted = True
                self.save()
        except IntegrityError:
            print('Could not deplete bonus')

    def give_login_bonus(self):
        try:
            with transaction.atomic():
                    self.bonus_money += self.casino_bonus_login
                    self.wagering()
                    self.save()
        except IntegrityError:
            print('Could not deplete bonus')

    def __repr__(self):
        return f'{self.__class__.__name__}' \
               f' {self.bonus_money}'


class Wallet(models.Model):
    real_money = models.FloatField(
        blank=False,
        null=False,
        default=0.0,
        help_text='Customer real amount'
                  ' of cash by deposits or wagered bonus.'
    )

    customer = models.ForeignKey(
        'CustomerUser',
        blank=False,
        null=True,
        on_delete=models.CASCADE
    )

    casino_bonus_deposit = models.FloatField(
        blank=False,
        null=False,
        default=20.0,
        help_text='Amount granted if customer '
                  'deposits larger than 100 euros'
    )

    deposit_bonus_amount = models.FloatField(
        blank=False,
        null=False,
        default=100.0,
        help_text='Amount of deposit to verify against. '
                  'If customer deposits an amount larger '
                  'than this field, we grant him a bonus of '
                  'the field casino_bonus_deposit'
    )

    def deposit_amount(self, amount: float) -> float:
        """
        Deposits amount and grants bonus if needed
        """
        bonus = Bonus()
        try:
            with transaction.atomic():
                # adds deposit to the amount
                self.real_money += abs(amount)
                if amount > self.deposit_bonus_amount:
                    # if amount is greater than
                    # x euros we grant customers a bonus
                    # bonus
                    bonus.customer = self.customer
                    bonus.bonus_money += self.casino_bonus_deposit
                    bonus.wagering()
                    bonus.save()
                self.save()
        except IntegrityError:
            print('Could not deposit')

        return self.real_money

    def spin(self, spin_amount: float) -> Tuple[float, float, str]:
        """
        Spins amounts. Takes spined amount from real wallet.
        Otherwise takes it from bunos wallet.
        """
        win_amount = spin_amount * 2
        choice = random.choice(['won', 'lost'])
        try:
            with transaction.atomic():
                if choice == 'won':
                    if self.real_money > 0:
                        self.real_money += win_amount
                    elif self.real_money == 0 and self.bonus.bonus_money > 0:
                        self.bonus.bonus_money += win_amount
                else:
                    if self.real_money > 0 and \
                            self.real_money >= spin_amount:
                        self.real_money -= spin_amount

                    if self.real_money == 0 and \
                            self.bonus.bonus_money >= spin_amount:
                        self.bonus.bonus_money -= spin_amount

                self.save()
        except IntegrityError:
            print('Could not spin amount')

        return win_amount, spin_amount, choice

    def __repr__(self):
        return f'{self.__class__.__name__}' \
               f' {self.real_money}'


class CustomerUser(User):
    # def save(self, *args, **kwargs):
    #     try:
    #         with transaction.atomic():
    #             wallet = Wallet()
    #             wallet.save()
    #
    #             bonus = Bonus()
    #             bonus.save()
    #
    #             self.wallet = wallet
    #             self.bonus = bonus
    #
    #             super(CustomerUser, self).save(*args, **kwargs)
    #
    #     except IntegrityError as exception:
    #         print(str(exception))

    def __repr__(self):
        return f'{self.__class__.__name__} {self.username}'
