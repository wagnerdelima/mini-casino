from unittest import TestCase
from unittest import mock

from django.db import IntegrityError

from model_mommy.mommy import make

from casino.models import Bonus
from casino.models import Wallet
from casino.models import CustomerUser


class BonusTestCase(TestCase):
    def setUp(self):
        self.user = make(CustomerUser)
        self.bonus = make(
            Bonus,
            bonus_money=30,
            customer=self.user
        )

    def tearDown(self):
        self.user.delete()
        self.bonus.delete()

    def test_bonus_wagering_success(self):
        rand_number = self.bonus.wagering()
        expected = rand_number * self.bonus.bonus_money

        self.assertEqual(self.bonus.wagering_requirement, expected)

    def test_is_depleted_fail(self):
        expected = self.bonus._is_depleted()
        self.assertFalse(expected)

    def test_is_depleted_success(self):
        self.bonus.bonus_money = 0
        expected = self.bonus._is_depleted()
        self.assertTrue(expected)

    def test_deplete_bonus_success(self):
        self.bonus.bonus_money = 0
        self.bonus.deplete_bonus()
        self.assertTrue(self.bonus.is_bonus_depleted)

    def test_deplete_bonus_exception_fail(self):
        with mock.patch('casino.models.transaction.atomic') \
                as mock_atomic:
            mock_atomic.side_effect = IntegrityError
            with mock.patch('casino.models.logging') as mock_log:
                self.bonus.deplete_bonus()
                self.assertFalse(self.bonus.is_bonus_depleted)
                mock_log.error.called_once()

    def test_give_login_bonus_success(self):
        bonus = make(Bonus, customer=self.user)
        bonus.give_login_bonus()
        self.assertEqual(
            bonus.casino_bonus_login,
            bonus.bonus_money
        )

        # grants bonus again
        bonus.give_login_bonus()
        self.assertEqual(
            bonus.casino_bonus_login * 2,
            bonus.bonus_money
        )

    def test_give_login_bonus_exception_fail(self):
        bonus = make(Bonus, customer=self.user)
        with mock.patch('casino.models.transaction.atomic') \
                as mock_atomic:
            mock_atomic.side_effect = IntegrityError
            with mock.patch('casino.models.logging') as mock_log:
                bonus.give_login_bonus()
                mock_log.error.called_once()
                self.assertEqual(0, bonus.bonus_money)

    def test_automatic_wagering_success(self):
        self.bonus.wagering()
        lost_amount = self.bonus.wagering_requirement + 1
        to_be_wagered = self.bonus.bonus_money
        wagered = self.bonus.automatic_wagering(lost_amount)

        self.assertEqual(0, self.bonus.bonus_money)
        self.assertEqual(to_be_wagered, wagered)
        self.assertTrue(self.bonus.is_bonus_depleted)

    def test_automatic_wagering_fail(self):
        self.bonus.wagering()

        lost_amount = self.bonus.wagering_requirement - 10
        wagered = self.bonus.automatic_wagering(lost_amount)

        self.assertEqual(0, wagered)

    def test__str__(self):
        self.assertEqual(
            f'{self.bonus.__class__.__name__}'
            f' {self.bonus.bonus_money}',
            self.bonus.__str__()
        )


class WalletTestCase(TestCase):
    def setUp(self):
        self.user = make(CustomerUser)

    def tearDown(self):
        self.user.delete()

    def test_deposit_amount_no_bonus_success(self):
        wallet = make(Wallet, customer=self.user)
        amount = 100
        expected = wallet.deposit_amount(amount)

        count_wallets = Wallet.objects.filter(customer=self.user).count()
        count_bonuses = Bonus.objects.filter(customer=self.user).count()

        self.assertEqual(amount, expected)
        self.assertEqual(amount, wallet.real_money)
        self.assertEqual(1, count_wallets)
        self.assertEqual(0, count_bonuses)

    def test_deposit_amount_with_bonus_success(self):
        wallet = make(Wallet, customer=self.user)
        amount = 110
        expected = wallet.deposit_amount(amount)

        count_wallets = Wallet.objects.filter(customer=self.user).count()
        count_bonus = Bonus.objects.filter(customer=self.user).count()
        bonus = Bonus.objects.get(customer=self.user)

        self.assertEqual(amount, expected)
        self.assertEqual(amount, wallet.real_money)
        self.assertEqual(amount, wallet.real_money)
        self.assertEqual(wallet.casino_bonus_deposit, bonus.bonus_money)
        self.assertEqual(1, count_wallets)
        self.assertEqual(1, count_bonus)

    def test_deposit_amount_negative_amount_success(self):
        wallet = make(Wallet, customer=self.user)
        amount = -100
        expected = wallet.deposit_amount(amount)
        self.assertEqual(abs(amount), expected)
        self.assertEqual(abs(amount), wallet.real_money)

    def test_deposit_amount_fail(self):
        with mock.patch('casino.models.transaction.atomic') \
                as mock_atomic:
            mock_atomic.side_effect = IntegrityError
            with mock.patch('casino.models.logging') as mock_log:
                wallet = make(Wallet, customer=self.user)
                wallet.deposit_amount(110)
                mock_log.error.called_once()

    def test_spin_win_with_real_money_success(self):
        deposit_amount = 200
        wallet = make(Wallet, customer=self.user)
        wallet.deposit_amount(deposit_amount)
        previous_money = wallet.real_money

        with mock.patch('casino.models.random.choice') as mock_choice:
            mock_choice.return_value = 'won'
            win, _, _ = wallet.spin()

            self.assertEqual(previous_money + win, wallet.real_money)

    def test_spin_win_with_bonus_money_success(self):
        deposit_amount = 200
        wallet = make(Wallet, customer=self.user)
        wallet.deposit_amount(deposit_amount)
        wallet.real_money = 0

        with mock.patch('casino.models.random.choice') as mock_choice:
            mock_choice.return_value = 'won'
            win, _, _ = wallet.spin()

            bonus = Bonus.objects.filter(
                bonus_money__gt=0,
                is_bonus_depleted=False
            ).order_by('-wagering_requirement')[0]

            self.assertEqual(
                wallet.casino_bonus_deposit + win,
                bonus.bonus_money
            )

    def test_spin_lose_with_real_money_success(self):
        deposit_amount = 200
        wallet = make(Wallet, customer=self.user)
        wallet.deposit_amount(deposit_amount)
        previous_money = wallet.real_money
        amount_lost = wallet.amount_lost

        with mock.patch('casino.models.random.choice') as mock_choice:
            mock_choice.return_value = 'lost'
            _, lost, _ = wallet.spin()

            self.assertEqual(previous_money - lost, wallet.real_money)
            self.assertEqual(amount_lost + lost, wallet.amount_lost)

    def test_spin_lose_with_bonus_money_success(self):
        deposit_amount = 200
        wallet = make(Wallet, customer=self.user)
        wallet.deposit_amount(deposit_amount)
        wallet.real_money = 0

        with mock.patch('casino.models.random.choice') as mock_choice:
            mock_choice.return_value = 'lost'
            _, lost, _ = wallet.spin()

            bonus = Bonus.objects.filter(
                bonus_money__gt=0,
                is_bonus_depleted=False
            ).order_by('-wagering_requirement')[0]

            self.assertEqual(
                wallet.casino_bonus_deposit - lost,
                bonus.bonus_money
            )

    def test_grant_wagered_success(self):
        amount = 100
        wallet = make(Wallet, customer=self.user)
        wallet.real_money = amount
        wallet.grant_wagered(amount)
        self.assertEqual(200, wallet.real_money)
