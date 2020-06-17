from rest_framework import routers

from apps.core.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='users')
urlpatterns = router.urls
