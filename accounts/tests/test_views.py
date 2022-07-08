import datetime

import pytz
from django.test import TestCase
from bs4 import BeautifulSoup
from django.core import mail
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from accounts.models import CustomUser, Country
from events.models import Event, Notification, CustomUserEvent


class TestCreateUser(TestCase):

    def setUp(self):
        Country.objects.create(country_name=None)
        Country.objects.create(country_name='Afghanistan')

    def test_create_custom_user_with_indicating_country(self):
        response = self.client.post(
            'http://localhost:8000/auth/users/', {
                'username': 'Test_User_1',
                'email': 'TestUser_1@gmail.com',
                'password': 'user1234',
                'country': 2
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_custom_user_without_indicating_country(self):
        response = self.client.post(
            'http://localhost:8000/auth/users/', {
                'username': 'Test_User_1',
                'email': 'TestUser_1@gmail.com',
                'password': 'user1234',
                'country': 1
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestActivateUser(TestCase):

    def setUp(self):
        call_command('create_country')
        self.client.post(
            'http://localhost:8000/auth/users/', {
                'username': 'TestUser_1',
                'email': 'TestUser_1@gmail.com',
                'password': 'user1234',
                'country': 2
            }
        )
        self.client.post(
            'http://localhost:8000/auth/users/', {
                'username': 'TestUser_2',
                'email': 'TestUser_2@gmail.com',
                'password': 'user1234',
                'country': 1
            }
        )

    def test_send_activation_email(self):
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].from_email, 'webmaster@localhost')
        self.assertEqual(mail.outbox[0].to, ['TestUser_1@gmail.com'])
        soup = BeautifulSoup(mail.outbox[0].html, features="lxml")
        self.assertTrue(soup.find('a').get('href'))

    def test_activate_email(self):
        soup = BeautifulSoup(mail.outbox[0].html, features="lxml")
        href = soup.find('a').get('href')
        token = href.split('/')[-1]
        uid = href.split('/')[-2]
        response = self.client.get(
            href,
            {"uid": uid, "token": token}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(CustomUser.objects.get(username='TestUser_1').is_active)


class TestApiUpdateCustomUserEvent(APITransactionTestCase):
    reset_sequences = True

    def setUp(self):
        country = Country.objects.create(country_name='Afghanistan')
        notification = Notification.objects.create(
            description='Do not deliver notification',
            value_time=None)
        event_1 = Event.objects.create(
            name='Afghanistan: Eid Al Adha Holiday',
            start_datetime=datetime.datetime(
                year=2023,
                month=6,
                day=30,
                hour=3,
                minute=0,
                tzinfo=pytz.UTC
            ),
            end_datetime=datetime.datetime(
                year=2023,
                month=7,
                day=1,
                hour=3,
                minute=0,
                tzinfo=pytz.UTC
            ),
            notification=notification,
            country_holiday=country,
            official_holiday=True
        )
        event_2 = Event.objects.create(
            name='Afghanistan: Eid al-Fitr Holiday',
            start_datetime=datetime.datetime(
                year=2023,
                month=4,
                day=23,
                hour=3,
                minute=0,
                tzinfo=pytz.UTC
            ),
            end_datetime=datetime.datetime(
                year=2023,
                month=4,
                day=24,
                hour=3,
                minute=0,
                tzinfo=pytz.UTC
            ),
            notification=notification,
            country_holiday=country,
            official_holiday=True
        )
        user = CustomUser.objects.create(
            username='TestUser_1',
            email='TestUser_1@gmail.com',
            password='user1234',
            country=country,
            is_active=True
        )
        CustomUserEvent.objects.create(user=user, event=event_1)
        CustomUserEvent.objects.create(user=user, event=event_2)

    def test_post_with_authenticate(self):
        user = CustomUser.objects.get(id=1)
        self.client.force_authenticate(user)
        response = self.client.post(reverse('update-custom-user-event'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_without_authenticate(self):
        response = self.client.post(reverse('update-custom-user-event'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_without_new_event(self):
        user = CustomUser.objects.get(id=1)
        self.client.force_authenticate(user)
        response = self.client.post(reverse('update-custom-user-event'))
        self.assertEqual(response.data, {'added_events': []})

    def test_post_with_new_event(self):
        country = Country.objects.get(id=1)
        notification = Notification.objects.get(id=1)
        Event.objects.create(
            name='Afghanistan: Liberation Day',
            start_datetime=datetime.datetime(
                year=2023,
                month=2,
                day=15,
                hour=3,
                minute=0,
                tzinfo=pytz.UTC
            ),
            end_datetime=datetime.datetime(
                year=2023,
                month=2,
                day=16,
                hour=3,
                minute=0,
                tzinfo=pytz.UTC
            ),
            notification=notification,
            country_holiday=country,
            official_holiday=True
        )
        user = CustomUser.objects.get(id=1)
        self.client.force_authenticate(user)
        response = self.client.post(reverse('update-custom-user-event'))
        self.assertEqual(response.data, {'added_events': ['Afghanistan: Liberation Day']})