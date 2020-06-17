from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'password',
            'username')


class UserViewSet(ModelViewSet):
    """
    User API used for listing of users
    and creating new user
    This is Admin only API
    Non staff user cant access this api.
    Check openapi.yaml for detailed request/response body
    """
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'head']
