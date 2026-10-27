from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User

class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("auth-register")
        self.login_url = reverse("auth-login")
        self.user_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "Password123!"
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "john.doe@example.com")
        self.assertEqual(response.data["name"], "John Doe")
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_register_duplicate_email_fails(self):
        self.client.post(self.register_url, self.user_data, format="json")
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_user_success(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            "email": "john.doe@example.com",
            "password": "Password123!"
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["email"], "john.doe@example.com")

    def test_login_with_wrong_password_fails(self):
        User.objects.create_user(**self.user_data)
        wrong_login_data = {
            "email": "john.doe@example.com",
            "password": "WrongPassword!"
        }
        response = self.client.post(self.login_url, wrong_login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_me_endpoint_requires_jwt(self):
        me_url = reverse("auth-me")
        # Without token
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # With token
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)
