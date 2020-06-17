from django.contrib.auth.models import User
from django.db.models import ExpressionWrapper, F, DurationField
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.book_rental.models import Book, RentedBook


class BookSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.get_full_name')
    category = serializers.CharField(source='category.name')

    class Meta:
        model = Book
        exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']


class BookViewSet(ReadOnlyModelViewSet):
    """
    Returns paginated list of books
    Default pagination size is 100
    """

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,
                              OAuth2Authentication,
                              SessionAuthentication,
                              TokenAuthentication)
    serializer_class = BookSerializer
    search_fields = ['name']

    def get_queryset(self):
        """
        select_related to avoid multiple db hits
        """
        return Book.objects.select_related(
            'category',
            'author',
        )


class RentedBookSerialiser(serializers.ModelSerializer):
    book_id = serializers.IntegerField()
    book_name = serializers.CharField(source='book.name')
    days_rented_for = serializers.CharField()
    total_charge = serializers.CharField()

    class Meta:
        model = RentedBook
        fields = ['book_name', 'book_id', 'days_rented_for',
                  'total_charge', 'rent_date', 'return_date']


class UserBooksAPIView(GenericAPIView):
    """
    Gives a User's rented books with charges and fine applied
    """
    serializer_class = RentedBookSerialiser
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,
                              OAuth2Authentication,
                              SessionAuthentication,
                              TokenAuthentication)

    def get_queryset(self):
        """
        queryset with prefetch_related for book and category
        """
        return RentedBook.objects.filter(user=self.kwargs['user_id']).annotate(
            time_spent=ExpressionWrapper(
                F('return_date') - F('rent_date'),
                output_field=DurationField()
            )
        ).prefetch_related('book')

    def get(self, request, user_id):

        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(detail="User not found")

        queryset = self.get_queryset()
        serialiser = RentedBookSerialiser(queryset, many=True)
        data = serialiser.data
        return Response(data, status=HTTP_200_OK)
