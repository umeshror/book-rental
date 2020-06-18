import datetime
from unittest.mock import patch, PropertyMock

from django.test.testcases import TestCase

from apps.book_rental.tests.factories import BookFactory, UserFactory, RentedBookFactory, CategoryFactory, \
    CategoryDayChargeFactory


class TestUsersBookSerializer(TestCase):

    def setUp(self):
        self.user = UserFactory()
        BookFactory.reset_sequence()

        self.fiction_cat = CategoryFactory(name='fiction')
        self.regular_cat = CategoryFactory(name='regular')
        self.novel_cat = CategoryFactory(name='novels')

        # delete default dayswise
        regular_dayswise1 = self.regular_cat.dayswise_charges.first()
        regular_dayswise1.delete()
        fiction_dayswise1 = self.fiction_cat.dayswise_charges.first()
        fiction_dayswise1.delete()
        novel_dayswise1 = self.novel_cat.dayswise_charges.first()
        novel_dayswise1.delete()

        self.fiction_rented = RentedBookFactory(
            user=self.user,
            book=BookFactory(name="Fiction book", category=self.fiction_cat),
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 5, 10))

        self.regular_rented = RentedBookFactory(
            user=self.user,
            book=BookFactory(name="Regular book", category=self.regular_cat),
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 4))

        self.novel_rented = RentedBookFactory(
            user=self.user,
            book=BookFactory(name="Novel book", category=self.novel_cat),
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 1))

    def test_days_rented(self):
        """
        Test if method gives correct days duration
        """
        self.assertEqual(self.fiction_rented.days_rented, 9)
        self.assertEqual(self.regular_rented.days_rented, 34)
        self.assertEqual(self.novel_rented.days_rented, 31)

        # change the rent_date
        self.fiction_rented.rent_date = datetime.date(2020, 5, 4)
        self.assertEqual(self.fiction_rented.days_rented, 6)

        # change the rent_date
        self.fiction_rented.return_date = datetime.date(2020, 5, 6)
        self.assertEqual(self.fiction_rented.days_rented, 2)

    def test_total_charge_fiction(self):
        """
        Test if method gives correct total charges for fiction

        days_from    days_to    per_day_charge  min_days   min_charge
        0              2            1              2           2
        3              31           1.5            5           4.5
        32             --           2              --          --
        """

        fiction_dayswise1 = CategoryDayChargeFactory(
            category=self.fiction_cat,
            days_from=0,
            days_to=2,
            per_day_charge=1,
            min_days=2,
            min_charge=2,
        )
        fiction_dayswise2 = CategoryDayChargeFactory(
            category=self.fiction_cat,
            days_from=3,
            days_to=30,
            per_day_charge=1.5,
            min_days=5,
            min_charge=4.5,
        )
        fiction_dayswise3 = CategoryDayChargeFactory(
            category=self.fiction_cat,
            days_from=31,
            per_day_charge=2,
        )
        with patch('apps.book_rental.models.RentedBook.days_rented',
                   new_callable=PropertyMock) as mock_days_rented:
            # days_rented =  1 days          2 (min_charge)
            mock_days_rented.return_value = 2
            self.assertEqual(self.fiction_rented.total_charge, 2)

            # days_rented =  4 days          2*1.0 + 4.5 (min_charge)
            mock_days_rented.return_value = 4
            self.assertEqual(self.fiction_rented.total_charge, 6.5)

            # days_rented =  9 days          2*1.0 + 7*1.5
            mock_days_rented.return_value = 9
            self.assertEqual(self.fiction_rented.total_charge, 12.5)

            # days_rented =  15 days          2*1.0 + 13*1.5
            mock_days_rented.return_value = 15
            self.assertEqual(self.fiction_rented.total_charge, 21.5)

            # days_rented =  30 days          2*1.0 + 28*1.5
            mock_days_rented.return_value = 30
            self.assertEqual(self.fiction_rented.total_charge, 44)


    def test_total_charge_regular(self):
        """
        Test if method gives correct total charges for regular

        days_from    days_to    per_day_charge  min_days   min_charge
        0              2            1              2           2
        3              --           1.5            --          --
        """
        regular_dayswise1 = CategoryDayChargeFactory(
            category=self.regular_cat,
            days_from=0,
            days_to=2,
            per_day_charge=1,
            min_days=2,
            min_charge=2,
        )
        regular_dayswise2 = CategoryDayChargeFactory(
            category=self.regular_cat,
            days_from=3,
            per_day_charge=1.5,
        )
        with patch('apps.book_rental.models.RentedBook.days_rented',
                   new_callable=PropertyMock) as mock_days_rented:
            # days_rented =  1 days          1 (min_charge)
            mock_days_rented.return_value = 1
            self.assertEqual(self.regular_rented.total_charge, 2.0)

            # days_rented =  2 days          2 * 1.0
            mock_days_rented.return_value = 2
            self.assertEqual(self.regular_rented.total_charge, 2.0)

            # days_rented =  6 days          2 * 1.0 + 4*1.5
            mock_days_rented.return_value = 6
            self.assertEqual(self.regular_rented.total_charge, 8.0)

    def test_total_charge_novel(self):
        """
        Test if method gives correct total charges for novel

        days_from    days_to    per_day_charge  min_days   min_charge
        0              3            1.5             3           4.5
        4              --           1.5             --          --
        """
        CategoryDayChargeFactory(
            category=self.novel_cat,
            days_from=0,
            days_to=3,
            per_day_charge=1.5,
            min_days=3,
            min_charge=4.5,
        )
        CategoryDayChargeFactory(
            category=self.novel_cat,
            days_from=4,
            per_day_charge=1.5,
        )
        with patch('apps.book_rental.models.RentedBook.days_rented',
                   new_callable=PropertyMock) as mock_days_rented:
            # days_rented =  1 days          4.5 (min_charge)
            mock_days_rented.return_value = 1
            self.assertEqual(self.novel_rented.total_charge, 4.5)

            # days_rented =  3 days          3 * 1.5
            mock_days_rented.return_value = 2
            self.assertEqual(self.novel_rented.total_charge, 4.5)

            # days_rented =  6 days          3 * 1.5 + 3*1.5
            mock_days_rented.return_value = 6
            self.assertEqual(self.novel_rented.total_charge, 9.0)
