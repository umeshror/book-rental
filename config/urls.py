"""auth_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView, TokenObtainPairView

from apps.landing_view import index

urlpatterns = [
    url(r'^$', index, name='index'),

    url('api/user/', include('apps.core.urls'), name='user_urls'),

    url('api/', include('apps.book_rental.urls'), name='book_rental_urls'),
    # admin
    path('admin/', admin.site.urls),

    # auth
    path('auth-token/', obtain_auth_token, name='api_token_auth'),
    # jwt
    path('jwt/token/', TokenObtainPairView.as_view(), name='jwt_token_obtain_pair'),
    path('jwt/token/refresh/', TokenRefreshView.as_view(), name='jwt_token_refresh'),
    path('jwt/token/verify/', TokenVerifyView.as_view(), name='jwt_token_verify'),
    # oauth2_provider
    path('oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
