from unittest import TestCase

from model_mommy.mommy import make

from casino.models import Bonus
from casino.models import CustomerUser


class BonusTestCase(TestCase):
    def setUp(self):
        user = make(CustomerUser)
        self.bonus = make(
            Bonus,
            bonus_money=30,
            customer=user
        )

    def test_bonus_wagering_success(self):
        rand_number = self.bonus.wagering()
        expected = rand_number * self.bonus.bonus_money

        self.assertEqual(expected, self.bonus.wagering_requirement)
