import datetime

from django.core.management.base import BaseCommand

from apps.book_rental.tests.factories import UserFactory, CategoryFactory, BookFactory, RentedBookFactory


class Command(BaseCommand):
    help = 'Seeds the database.'

    def add_arguments(self, parser):
        parser.add_argument('--books',
                            default=150,
                            type=int,
                            help='The number of fake books to create.')

    def handle(self, *args, **options):
        UserFactory(username='webadmin', is_staff=True)

        user1 = UserFactory(is_staff=True)
        user2 = UserFactory()

        novel_cat = CategoryFactory(
            name='novels',
            per_day_charge=1.5,
        )
        regular_cat = CategoryFactory(
            name='regular',
            per_day_charge=1.5,
        )
        fiction_cat = CategoryFactory(
            name='fiction',
            per_day_charge=3,
        )

        fiction_book = BookFactory(name="Fiction book",
                                   category=fiction_cat)

        regular_book = BookFactory(name="Regular book",
                                   category=regular_cat)

        novel_book = BookFactory(name="Novel book",
                                 category=novel_cat)

        RentedBookFactory(
            user=user1,
            book=fiction_book,
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 5, 10)
        )
        RentedBookFactory(
            user=user1,
            book=regular_book,
            rent_date=datetime.date(2020, 5, 1),
        )

        RentedBookFactory(
            user=user1,
            book=novel_book,
            rent_date=datetime.date(2020, 5, 1),
            return_date=datetime.date(2020, 6, 1)
        )

        RentedBookFactory(
            user=user2,
            book=regular_book,
            rent_date=datetime.date(2019, 5, 1),
            return_date=datetime.date(2020, 5, 1)
        )

        RentedBookFactory(
            user=user2,
            book=novel_book,
            rent_date=datetime.date(2019, 5, 1),
            return_date=datetime.date(2020, 5, 1)
        )
