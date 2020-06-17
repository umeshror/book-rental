from rest_framework import serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from apps.book_rental.models import Book


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
    authentication_classes = (OAuth2Authentication, SessionAuthentication, TokenAuthentication)
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
