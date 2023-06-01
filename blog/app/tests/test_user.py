from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import User
from app.tests.factories import UserFactory


class TestUserView(APITestCase):
    """Test for user views"""

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('thepassword')
        self.user.is_verified = True
        self.user.save()

    def test_case_get_user(self):
        """Testing the retrieve of a user info"""
        self.url = reverse('app:user')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.first_name, response.json()['first_name'])
        self.assertEqual(user.last_name, response.json()['last_name'])
        self.assertEqual(user.email, response.json()['email'])
        self.assertEqual(user.username, response.json()['username'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
