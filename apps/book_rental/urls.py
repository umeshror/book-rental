from django.conf.urls import url
from rest_framework import routers

from apps.book_rental.views import BookViewSet, UserBooksAPIView

router = routers.DefaultRouter()
router.register(r'books', BookViewSet, basename='books')
urlpatterns = router.urls

urlpatterns += [
    url(r'^user-books/(?P<user_id>[0-9]+)/$', UserBooksAPIView.as_view(),
        name='user-books'),
]
