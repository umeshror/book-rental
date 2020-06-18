import datetime

from django.core.management.base import BaseCommand

from apps.book_rental.tests.factories import UserFactory, CategoryFactory, BookFactory, RentedBookFactory, \
    CategoryDayChargeFactory


class Command(BaseCommand):
    help = 'Seeds the database.'

    def add_arguments(self, parser):
        parser.add_argument('--books',
                            default=150,
                            type=int,
                            help='The number of fake books to create.')

    def handle(self, *args, **options):
        user1 = UserFactory(first_name='User 1',
                            username='admin',
                            is_superuser=True,
                            is_staff=True)
        user1.set_password('admin123')
        user1.save()

        user2 = UserFactory(first_name='User 2', is_staff=True)
        user3 = UserFactory(first_name='User 3')

        novel_cat = CategoryFactory(name='novels')
        novel_dayswise1 = novel_cat.dayswise_charges.first()
        novel_dayswise1.delete()

        novel_dayswise1 = CategoryDayChargeFactory(
            category=novel_cat,
            days_from=0,
            days_to=3,
            per_day_charge=1.5,
            min_days=3,
            min_charge=4.5,
        )
        novel_dayswise2 = CategoryDayChargeFactory(
            category=novel_cat,
            days_from=4,
            per_day_charge=1.5,
        )

        regular_cat = CategoryFactory(name='regular')
        regular_dayswise1 = regular_cat.dayswise_charges.first()
        regular_dayswise1.delete()

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

        fiction_cat = CategoryFactory(name='fiction')
        fiction_dayswise1 = fiction_cat.dayswise_charges.first()
        fiction_dayswise1.delete()

        fiction_dayswise1 = CategoryDayChargeFactory(
            category=fiction_cat,
            days_from=0,
            days_to=2,
            per_day_charge=1,
            min_days=2,
            min_charge=2,
        )
        fiction_dayswise2 = CategoryDayChargeFactory(
            category=fiction_cat,
            days_from=3,
            days_to=30,
            per_day_charge=1.5,
            min_days=5,
            min_charge=4.5,
        )
        fiction_dayswise3 = CategoryDayChargeFactory(
            category=fiction_cat,
            days_from=31,
            per_day_charge=2,
        )

        fiction_book = BookFactory(name="Fiction book",
                                   category=fiction_cat)

        regular_book = BookFactory(name="Regular book",
                                   category=regular_cat)

        novel_book = BookFactory(name="Novel book",
                                 category=novel_cat)

        RentedBookFactory(
            user=user2,
            book=fiction_book,
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 5, 10)
        )
        RentedBookFactory(
            user=user2,
            book=regular_book,
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 4)
        )

        RentedBookFactory(
            user=user2,
            book=novel_book,
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 1)
        )

        RentedBookFactory(
            user=user3,
            book=regular_book,
            rent_date=datetime.date(2019, 5, 1),
            return_date=datetime.date(2020, 5, 1)
        )

        RentedBookFactory(
            user=user3,
            book=novel_book,
            rent_date=datetime.date(2019, 5, 1),
            return_date=datetime.date(2020, 5, 1)
        )
