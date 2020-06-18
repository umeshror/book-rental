import datetime

from django.test.testcases import TestCase

from apps.book_rental.tests.factories import BookFactory, UserFactory, RentedBookFactory


class TestUsersBookSerializer(TestCase):

    def setUp(self):
        self.user = UserFactory()
        BookFactory.reset_sequence()
        self.rented_book = RentedBookFactory(
            user=self.user,
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 1)
        )

    def test_days_rented_for(self):
        """
        Test if method gives correct days duration
        """
        self.assertEqual(self.rented_book.days_rented_for, 31)

        # change the rent_date
        self.rented_book.rent_date = datetime.date(2020, 5, 4)
        self.assertEqual(self.rented_book.days_rented_for, 28)

        # change the rent_date
        self.rented_book.return_date = datetime.date(2020, 5, 6)
        self.assertEqual(self.rented_book.days_rented_for, 2)

    def test_total_charge(self):
        """
        Test if method gives correct total charges
        """
        self.assertEqual(self.rented_book.total_charge, 31.0)

        # change per_day_charge for the selected rented book
        self.rented_book.book.category.per_day_charge = 2
        self.assertEqual(self.rented_book.total_charge, 62.0)

        # add fine selected rented book
        self.rented_book.fine_charged = 11.5
        self.assertEqual(self.rented_book.total_charge, 73.5)
