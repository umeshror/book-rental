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
        user1 = UserFactory(first_name='User 1',
                            username='admin',
                            is_superuser=True,
                            is_staff=True)
        user1.set_password('admin123')
        user1.save()
        user2 = UserFactory(first_name='User 2',
                            is_staff=True)
        user3 = UserFactory(first_name='User 3')

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
