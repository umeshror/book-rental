from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.views import UserSerializer


class TestUserSetup(TestCase):

    def setUp(self):
        self.user = User.objects.create(first_name="test_name",
                                        last_name="test_last_name",
                                        email="test@lastname.com",
                                        is_staff=True,
                                        username="test_username")


class TestUserAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create(first_name="test_name",
                                        last_name="test_last_name",
                                        email="test@lastname.com",
                                        is_staff=True,
                                        username="test_username")

    def test_create_user_by_staff(self):
        """
        Staff has logged in and trying to create user
        with all valid data
        """
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('users-list'),
                                    data={'first_name': "test_name",
                                          'username': "firstnameexamplecom",
                                          'email': "first_name@example.com",
                                          'last_name': "test_last_name",
                                          'password': 'admin123'})
        self.assertEqual(response.status_code, 201)

    def test_create_user_by_non_staff(self):
        """
        Normal user(non staff) has logged in and trying to create user
        with all valid data
        """
        self.user.is_staff = False
        self.user.save()

        self.client.force_login(user=self.user)
        response = self.client.post(reverse('users-list'),
                                    data={'first_name': "test_name",
                                          'username': "firstnameexamplecom",
                                          'email': "first_name@example.com",
                                          'last_name': "test_last_name",
                                          'password': 'admin123'})
        self.assertEqual(response.status_code, 403)

    def test_create_user_by_staff_error(self):
        """
        Normal user(non staff) has logged in and trying to create user
        with all valid data
        """

        self.client.force_login(user=self.user)
        response = self.client.post(reverse('users-list'),
                                    data={'first_name': "test_name",
                                          'email': "first_nameexample.com",
                                          'last_name': "test_last_name",
                                          'password': 'admin123'})
        self.assertEqual(response.status_code, 400)

    def test_list_users(self):
        """
        Test list of users api response
        """
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('users-list'), format='json')
        self.assertEqual(response.status_code, 200)


class TestUserSerializer(APITestCase):
    def setUp(self):
        self.user = User.objects.create(first_name="test_name",
                                        last_name="test_last_name",
                                        email="test@lastname.com",
                                        is_staff=True,
                                        username="test_username")

    def test_serializer_get(self):
        """
        Test Serialiser response for single get user
        """
        expected_output = {'email': 'test@lastname.com',
                           'first_name': 'test_name',
                           'last_name': 'test_last_name',
                           'id': self.user.id}

        ser = UserSerializer(instance=self.user)
        actual_output = ser.data
        self.assertEqual(expected_output, actual_output)

    def test_serializer_create_user(self):
        """
        Test Serialiser response for create user data
        """
        create_data = {'first_name': "test_name",
                       'username': "firstnameexamplecom",
                       'email': "first_name@example.com",
                       'last_name': "test_last_name",
                       'password': 'admin123'}

        ser = UserSerializer(data=create_data)
        ser.is_valid()
        user_instance = ser.save()
        self.assertIsInstance(user_instance, User)
        self.assertEqual(user_instance.email, "first_name@example.com")
