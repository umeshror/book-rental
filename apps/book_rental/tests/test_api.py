import datetime

from django.test.testcases import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.book_rental.tests.factories import BookFactory, UserFactory, RentedBookFactory, CategoryFactory, \
    CategoryDayChargeFactory
from apps.book_rental.views import BookSerializer, RentedBookSerialiser


class TestBookSerializer(TestCase):

    def setUp(self):
        self.user = UserFactory(is_staff=True)
        self.author = UserFactory()
        BookFactory.reset_sequence()

        self.book = BookFactory(author=self.author,
                                name="Da Vinci Code",
                                category__name='fiction',
                                created_by=self.user)

    def test_serialiser_response(self):
        serialiser = BookSerializer(instance=self.book)
        actual_response = serialiser.data
        expected_response = {'id': 1,
                             'author': self.author.get_full_name(),
                             'category': 'fiction',
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
        self.assertEqual(response_data['next'], 'http://testserver/api/books/?limit=100&offset=100')

    def test_detail_api(self):
        """
        Test Retrive API for first book
        Response is tested in Serialiser test cases
        """
        book = self.books[0]
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('books-detail', kwargs={'pk': book.id}))
        self.assertEqual(response.status_code, 200)


class TestUsersBookSerializer(TestCase):

    def setUp(self):
        self.user = UserFactory()
        BookFactory.reset_sequence()
        self.rented_book_1 = RentedBookFactory(
            user=self.user,
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 1)
        )

    def test_get_serialiser_response(self):
        """
        Test for single rented books response
        """
        serialiser = RentedBookSerialiser(self.rented_book_1)
        actual_response = serialiser.data
        expected_response = {'book_name': 'Book name 0',
                             'book_id': 1,
                             'days_rented': '31',
                             'total_charge': '31.0',
                             'rent_date': '2020-05-01',
                             'return_date': '2020-06-01'}
        self.assertEqual(actual_response, expected_response)

    def test_list_serialiser_response(self):
        """
        Test for multiple rented books response
        """
        self.rented_book_2 = RentedBookFactory(
            user=self.user,
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 5, 10),
            fine_charged=1.2
        )
        serialiser = RentedBookSerialiser([self.rented_book_1, self.rented_book_2], many=True)
        actual_response = serialiser.data
        expected_response = [{'book_name': 'Book name 0',
                              'book_id': 1,
                              'days_rented': '31',
                              'total_charge': '31.0',
                              'rent_date': '2020-05-01',
                              'return_date': '2020-06-01'},
                             {'book_name': 'Book name 1',
                              'book_id': 2,
                              'days_rented': '9',
                              'total_charge': '10.2',
                              'rent_date': '2020-05-01',
                              'return_date': '2020-05-10'}]
        self.assertEqual(actual_response, expected_response)


class TestUserBooksAPI(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        BookFactory.reset_sequence()

        novel_cat = CategoryFactory(name='novels')
        regular_cat = CategoryFactory(name='regular')
        fiction_cat = CategoryFactory(name='fiction')

        fiction_book = BookFactory(name="Fiction book", category=fiction_cat)
        regular_book = BookFactory(name="Regular book", category=regular_cat)
        novel_book = BookFactory(name="Novel book", category=novel_cat)

        regular_dayswise1 = regular_cat.dayswise_charges.first()
        regular_dayswise1.delete()
        fiction_dayswise1 = fiction_cat.dayswise_charges.first()
        fiction_dayswise1.delete()
        novel_dayswise1 = novel_cat.dayswise_charges.first()
        novel_dayswise1.delete()

        fiction_dayswise1 = CategoryDayChargeFactory(
            category=fiction_cat, days_from=0, days_to=2,
            per_day_charge=1, min_days=2, min_charge=2,
        )

        fiction_dayswise2 = CategoryDayChargeFactory(
            category=fiction_cat, days_from=3, days_to=30,
            per_day_charge=1.5, min_days=5, min_charge=4.5,
        )
        fiction_dayswise3 = CategoryDayChargeFactory(
            category=fiction_cat, days_from=31, per_day_charge=2,
        )
        regular_dayswise1 = CategoryDayChargeFactory(
            category=regular_cat,
            days_from=0,
            days_to=2,
            per_day_charge=1,
            min_days=2,
            min_charge=2,
        )
        regular_dayswise2 = CategoryDayChargeFactory(
            category=regular_cat,
            days_from=3,
            per_day_charge=1.5,
        )
        CategoryDayChargeFactory(
            category=novel_cat,
            days_from=0,
            days_to=3,
            per_day_charge=1.5,
            min_days=3,
            min_charge=4.5,
        )
        CategoryDayChargeFactory(
            category=novel_cat,
            days_from=4,
            per_day_charge=1.5,
        )
        RentedBookFactory(user=self.user,
                          book=fiction_book,
                          rent_date=datetime.date(2020, 5, 1),
                          return_date=datetime.date(2020, 5, 10))

        RentedBookFactory(user=self.user,
                          book=regular_book,
                          rent_date=datetime.date(2020, 5, 1),
                          return_date=datetime.date(2020, 6, 4))

        RentedBookFactory(user=self.user,
                          book=novel_book,
                          rent_date=datetime.date(2020, 5, 1),
                          return_date=datetime.date(2020, 6, 1))

    def test_get_api(self):
        """
        Test status code, (e2e)
        Cat 1

        """
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('user-books', kwargs={'user_id': self.user.id}))
        expected_response = [{'book_name': 'Fiction book',
                              'book_id': 1,
                              'days_rented': '9',
                              'total_charge': '12.5',
                              'rent_date': '2020-05-01',
                              'return_date': '2020-05-10'},
                             {'book_name': 'Regular book',
                              'book_id': 2,
                              'days_rented': '34',
                              'total_charge': '50.0',
                              'rent_date': '2020-05-01',
                              'return_date': '2020-06-04'},
                             {'book_name': 'Novel book',
                              'book_id': 3,
                              'days_rented': '31',
                              'total_charge': '46.5',
                              'rent_date': '2020-05-01',
                              'return_date': '2020-06-01'}]

        actual_response = response.json()
        self.assertEqual(actual_response, expected_response)
        self.assertEqual(response.status_code, 200)
