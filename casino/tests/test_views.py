from django.test import TestCase, Client
from django.urls import reverse

from unittest import mock

from model_mommy.mommy import make

from casino.models import Bonus, Wallet
from casino.models import CustomerUser
from casino.views import sum_bonuses


class ViewTestCase(TestCase):
    def setUp(self):
        self.user = make(CustomerUser)
        self.user.set_password('password')
        self.user.save()

        self.wallet = make(Wallet, customer=self.user)
        # deposits and creates bonus
        self.wallet.deposit_amount(110)

        self.client = Client()

    def test_sum_bonuses(self):
        bonus1 = Bonus(bonus_money=120, customer=self.user)
        bonus2 = Bonus(bonus_money=42, customer=self.user)
        bonus1.save()
        bonus2.save()

        result, bonus_result = sum_bonuses(self.user.id)
        self.assertEqual(
            self.wallet.casino_bonus_deposit + 162,
            result
        )

    def test_index_no_authentication_view_success(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'index.html')

    def test_index_is_authenticated_view_success(self):
        url = reverse('index')
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, self.wallet.real_money)

    def test_logout_is_authenticated_success(self):
        url = reverse('logout')
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_register_success(self):
        url = reverse('casino:register')
        response = self.client.post(
            url,
            data={
                'username': 'user',
                'password': 'pass',
                'confirm_password': 'pass   '
            }
        )
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'registration.html')
        self.assertContains(response, 'Go to dashboard')

    def test_register_invalid_fail(self):
        url = reverse('casino:register')
        with mock.patch('casino.views.logging') as mock_log:
            response = self.client.post(
                url,
                data={
                    'username': 'user',
                    'b': 'pass',
                    'a': 'pass   '
                }
            )
            self.assertEqual(200, response.status_code)
            mock_log.error.called_once()

    def test_register_get_do_not_register_success(self):
        url = reverse('casino:register')
        response = self.client.get(
            url
        )
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'registration.html')
        self.assertContains(response, 'Just fill out the form')
