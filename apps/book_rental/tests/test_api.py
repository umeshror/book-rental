from rest_framework.test import APITestCase

from apps.book_rental.tests.factories import BookFactory, UserFactory
from apps.book_rental.views import BookSerializer

from django.test.testcases import TestCase

from django.urls import reverse


class TestBookSerializer(TestCase):

    def setUp(self):
        self.user = UserFactory(is_staff=True)
        self.author = UserFactory()
        BookFactory.reset_sequence()

        self.book = BookFactory(author=self.author,
                                name="Da Vinci Code",
                                category__name='Fiction',
                                created_by=self.user)

    def test_serialiser_response(self):
        serialiser = BookSerializer(instance=self.book)
        actual_response = serialiser.data
        expected_response = {'id': 1,
                             'author': self.author.get_full_name(),
                             'category': 'Fiction',
                             'name': 'Da Vinci Code',
                             'slug': 'da-vinci-code',
                             'description': 'description_0',
                             'book_quantity': 0}
        self.assertEqual(actual_response, expected_response)


class TestBookAPI(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.books = BookFactory.create_batch(102)

    def test_list_api(self):
        """
        Test if paginated response gives exact count and urls
        Response is tested in Serialiser test cases
        """
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('books-list'))
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['count'], 102)
        self.assertEqual(response_data['next'], 'http://testserver/api/book_rental/books/?limit=100&offset=100')

    def test_detail_api(self):
        """
        Test Retrive API for first book
        Response is tested in Serialiser test cases
        """
        book = self.books[0]
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('books-detail', kwargs={'pk': book.id}))
        self.assertEqual(response.status_code, 200)
