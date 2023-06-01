from django.urls import reverse
from rest_framework.test import APITestCase


class TestSignUpView(APITestCase):
    """Test for initial signup view"""
    def setUp(self):
        self.url = reverse('app:session-signup')

    def test_user_is_created_sucessful(self):
        """Test successful user creation"""

        data = {
            "email": "jane.doe@example.com",
            "first_name": "jane",
            "last_name": "doe",
            "username": "janedoe",
            "password": "thepassword"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_user_fail_with_same_email(self):
        """Test failed user creation because of the email"""

        data = {
            "email": "jane.doe@example.com",
            "first_name": "jane",
            "last_name": "doe",
            "username": "janedoe",
            "password": "thepassword"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)

        data = {
            "email": "jane.doe@example.com",
            "first_name": "jack",
            "last_name": "sparrow",
            "username": "jasparrow",
            "password": "thepassword"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors'][0]['detail'], 'A user with that email already exists.')
        self.assertEqual(response.json()['errors'][0]['attr'], 'email')

    def test_user_fail_with_same_username(self):
        """Test failed user creation because of the username"""

        data = {
            "email": "jane.doe@example.com",
            "first_name": "jane",
            "last_name": "doe",
            "username": "janedoe",
            "password": "thepassword"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)

        data = {
            "email": "jack.sparrow@example.com",
            "first_name": "jack",
            "last_name": "sparrow",
            "username": "janedoe",
            "password": "thepassword"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errors'][0]['detail'], 'user with this username already exists.')
        self.assertEqual(response.json()['errors'][0]['attr'], 'username')
