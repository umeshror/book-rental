import datetime

from django.test.testcases import TestCase

from apps.book_rental.tests.factories import BookFactory, UserFactory, RentedBookFactory, CategoryFactory


class TestUsersBookSerializer(TestCase):

    def setUp(self):
        self.user = UserFactory()
        BookFactory.reset_sequence()

        fiction_cat = CategoryFactory(name='fiction', per_day_charge=3)
        regular_cat = CategoryFactory(name='regular', per_day_charge=1.5)
        novel_cat = CategoryFactory(name='novels', per_day_charge=1.5)

        self.fiction_rented = RentedBookFactory(
            user=self.user,
            book=BookFactory(name="Fiction book", category=fiction_cat),
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 5, 10))

        self.regular_rented = RentedBookFactory(
            user=self.user,
            book=BookFactory(name="Regular book", category=regular_cat),
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 4))

        self.novel_rented = RentedBookFactory(
            user=self.user,
            book=BookFactory(name="Novel book", category=novel_cat),
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 1))

    def test_days_rented_for(self):
        """
        Test if method gives correct days duration
        """
        self.assertEqual(self.fiction_rented.days_rented_for, 9)
        self.assertEqual(self.regular_rented.days_rented_for, 34)
        self.assertEqual(self.novel_rented.days_rented_for, 31)

        # change the rent_date
        self.fiction_rented.rent_date = datetime.date(2020, 5, 4)
        self.assertEqual(self.fiction_rented.days_rented_for, 6)

        # change the rent_date
        self.fiction_rented.return_date = datetime.date(2020, 5, 6)
        self.assertEqual(self.fiction_rented.days_rented_for, 2)

    def test_total_charge_fiction(self):
        """
        Test if method gives correct total charges for fiction
        """
        #  3 rs per day * 9 days
        self.assertEqual(self.fiction_rented.total_charge, 27)

        # change per_day_charge for the selected rented book
        #  2 rs per day * 9 days
        self.fiction_rented.book.category.per_day_charge = 2
        self.assertEqual(self.fiction_rented.total_charge, 18)

        # add fine selected rented book
        #  2 rs per day * 9 days + 11.5
        self.fiction_rented.fine_charged = 11.5
        self.assertEqual(self.fiction_rented.total_charge, 29.5)

    def test_total_charge_regular(self):
        """
        Test if method gives correct total charges for regular
        """
        #  1.5 rs per day * 34 days
        self.assertEqual(self.regular_rented.total_charge, 51.0)

        # change per_day_charge for the selected rented book
        #  2 rs per day * 34 days
        self.regular_rented.book.category.per_day_charge = 2
        self.assertEqual(self.regular_rented.total_charge, 68)

        # add fine selected rented book
        #  2 rs per day * 34 days + 11.5
        self.regular_rented.fine_charged = 11.5
        self.assertEqual(self.regular_rented.total_charge, 79.5)

    def test_total_charge_novel(self):
        """
        Test if method gives correct total charges for novel
        """
        #  1.5 rs per day * 31 days
        self.assertEqual(self.regular_rented.total_charge, 51.0)

        # change per_day_charge for the selected rented book
        #  2 rs per day * 31 days
        self.regular_rented.book.category.per_day_charge = 2
        self.assertEqual(self.regular_rented.total_charge, 68)

        # add fine selected rented book
        #  2 rs per day * 31 days + 11.5
        self.regular_rented.fine_charged = 11.5
        self.assertEqual(self.regular_rented.total_charge, 79.5)
