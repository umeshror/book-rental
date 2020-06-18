import datetime

import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from apps.book_rental.models import Category, Book, RentedBook


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: 'user_{}'.format(n))
    first_name = factory.Sequence(lambda n: 'first_{}'.format(n))
    last_name = factory.Sequence(lambda n: 'last_{}'.format(n))
    email = factory.LazyAttribute(lambda a: '{0}.{1}@example.com'.format(a.first_name, a.last_name).lower())
    password = "pass123"


class CategoryFactory(DjangoModelFactory):
    name = factory.fuzzy.FuzzyChoice(["regular", "fiction", "novels"])
    created_by = factory.SubFactory(UserFactory)
    per_day_charge = 1.0

    class Meta:
        model = Category
        django_get_or_create = ('name',)


class BookFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Book name {}'.format(n))
    description = factory.Sequence(lambda n: 'description_{}'.format(n))

    book_quantity = factory.Sequence(lambda n: n)
    category = factory.SubFactory(CategoryFactory)
    author = factory.SubFactory(UserFactory)
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Book
        django_get_or_create = ('name',)


class RentedBookFactory(DjangoModelFactory):
    book = factory.SubFactory(BookFactory)
    user = factory.SubFactory(UserFactory)
    created_by = factory.SubFactory(UserFactory)
    rent_date = factory.Sequence(lambda n: datetime.date(2020, 1, 1) + datetime.timedelta(days=n))
    return_date = factory.Sequence(lambda n: datetime.date(2020, 2, 1) + datetime.timedelta(days=n))

    class Meta:
        model = RentedBook


