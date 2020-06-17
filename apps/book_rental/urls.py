from rest_framework import routers

from apps.book_rental.views import BookViewSet

router = routers.DefaultRouter()
router.register(r'books', BookViewSet, basename='books')
urlpatterns = router.urls
