from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from app.tests.factories import UserFactory


class LoginTest(APITestCase):
    """Verify the loging tests"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password('thepassword')
        self.user.is_verified = True
        self.user.save()
        self.request = {'username': self.user.username, 'password': 'thepassword'}
        self.client = APIClient()
        self.url = reverse('app:session-login')

    def test_login_user_correct_credentials(self):
        """Test login user with correct credentials."""
        response = self.client.post(self.url, self.request, format='json')

        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_incorrect_credentials_password(self):
        """Test login user with bad password."""
        data = {
            'username': self.user.username,
            'password': 'bad_password'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['errors'][0]['detail'], 'Invalid credentials, try again')

    def test_login_user_incorrect_credentials_phone_number(self):
        """Test login user with bad phone."""

        data = {
            'username': 'bad_username',
            'password': 'thepassword'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['errors'][0]['detail'], 'Invalid credentials, try again')
