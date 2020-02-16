from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User, Group, UserManager
from rest_framework import serializers, filters , generics, viewsets
from rideshare.serializers import UserSerializer, RideShareSerializer, Db
from . import models
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

# UserManager.create_user()
class RideshareViewSet(viewsets.ModelViewSet):
    queryset = models.Rides.objects.all()
    serializer_class = RideShareSerializer

class RideshareViewSearch(generics.ListAPIView):
    queryset = models.Rides.objects.all()
    serializer_class = RideShareSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ('source','destination')
    
