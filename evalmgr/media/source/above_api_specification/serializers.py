from django.contrib.auth.models import User,UserManager
from rest_framework import serializers, filters , generics
from django.contrib.auth.hashers import make_password
from . import models
import django_filters

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups','password']

    validate_password = make_password   

class RideShareSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Rides
        fields = ['created_by','timestamp','source','destination']
    
