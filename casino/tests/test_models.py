from unittest import TestCase
from unittest import mock

from django.db import IntegrityError

from model_mommy.mommy import make

from casino.models import Bonus
from casino.models import CustomerUser


class BonusTestCase(TestCase):
    def setUp(self):
        self.user = make(CustomerUser)
        self.bonus = make(
            Bonus,
            bonus_money=30,
            customer=self.user
        )

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
        with mock.patch('casino.models.transaction.atomic')\
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
        with mock.patch('casino.models.transaction.atomic')\
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
