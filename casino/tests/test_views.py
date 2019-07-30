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
        self.deposit_amount = 110
        self.wallet.deposit_amount(self.deposit_amount)

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

    def test_login_user_success(self):
        url = reverse('casino:login_user')
        response = self.client.post(
            url,
            data={
                'username': self.user.username,
                'password': 'password',
            },
            follow=True
        )
        self.assertEqual(200, response.status_code)
        self.assertContains(response, f'Hello {self.user.username}')
        self.assertTemplateNotUsed('index.html')

    def test_login_inactive_user_fail(self):
        self.user.is_active = False
        self.user.save()
        url = reverse('casino:login_user')
        response = self.client.post(
            url,
            data={
                'username': self.user.username,
                'password': 'password',
            },
            follow=True
        )
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'You have provided wrong credentials')

    def test_login_page_renders_success(self):
        url = reverse('casino:login_user')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateNotUsed('index.html')

    def test_deposits_success(self):
        url = reverse('casino:deposit')
        self.client.login(username=self.user.username, password='password')
        response = self.client.post(
            url,
            data={'amount': 120},
            follow=True
        )

        wallet = Wallet.objects.get(customer=self.user)
        self.assertEqual(120 + self.deposit_amount, wallet.real_money)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed('index.html')

    def test_spin(self):
        url = reverse('casino:spin')
        self.client.login(username=self.user.username, password='password')
        response = self.client.post(url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed('index.html')
