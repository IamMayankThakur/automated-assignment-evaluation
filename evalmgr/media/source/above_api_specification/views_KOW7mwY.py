from django.shortcuts import render

from django.http import HttpResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from .models import  User, User_rides, Ride
from .serializers import UserSerializer, User_rideSerializer, RideSerializer
from rest_framework.response import Response
import requests
import json
import datetime
from rest_framework.decorators import api_view
import re
import pandas as pd
from django.core.serializers import serialize



re_password = re.compile("^[0-9A-Fa-f]{40}$")

def string_convert(old_date):
    old_date = old_date.split(":")
    d, m, y = old_date[0].split("-")
    s, mi, h = old_date[1].split("-")
    print(y+"-"+m+"-"+d+" "+h+":"+mi+":"+s)
    return y+"-"+m+"-"+d+" "+h+":"+mi+":"+s

def string_convert_reverse(new_date):
    new_date = new_date.split("T")
    y, m, d = new_date[0].split("-")
    h, mi, s = new_date[1].split(":")
    return d+"-"+m+"-"+y+":"+s[:len(s)-1]+"-"+mi+"-"+h

class usersList(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many = True)
        return Response(serializer.data)
    def put(self,request):
        if(re_password.match(request.data["password"])):
            r=requests.post("http://127.0.0.1:8000/api/v1/db/write",json={"table":"User","insert":request.data})
            if (r.status_code==200):
                return Response({},status=status.HTTP_201_CREATED)
            else:
                return Response({},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({},status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,user,format=None):
        user_ = User.objects.filter(username=user)
        if len(user_)==0:
            return Response({},status=status.HTTP_400_BAD_REQUEST)
        else:
            user_.delete()
            return Response({},status=status.HTTP_200_OK)

class ridesList(APIView):
    def get(self, request):
        source = int(request.GET['source'])
        destination = int(request.GET['destination'])
        data = pd.read_csv("C:/Users/Akanksha/Documents/sem6/CC/A1/Rachana/assignment1/rideshare/AreaNameEnum.csv")
        print(type(source))
        if (source != destination):
            if(source in data["Area No"]) and (destination in data["Area No"]):
                rides = Ride.objects.filter(source=source, destination=destination, timestamp__gte=datetime.datetime.now())
                if(len(rides)==0):
                    return Response({}, status=status.HTTP_204_NO_CONTENT)
                serializer = RideSerializer(rides, many = True)
                for i in range(len(rides)):
                    serializer.data[i]["username"] = serializer.data[i]["created_by"]
                    serializer.data[i]["timestamp"] = string_convert_reverse(serializer.data[i]["timestamp"])
                    del serializer.data[i]["created_by"], serializer.data[i]["source"], serializer.data[i]["destination"]
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({},status=status.HTTP_400_BAD_REQUEST)
    def post(self,request):
        data = pd.read_csv("C:/Users/Akanksha/Documents/sem6/CC/A1/Rachana/assignment1/rideshare/AreaNameEnum.csv")
        source = request.data["source"]
        destination = request.data["destination"]
        if (source != destination):
            if(source in data["Area No"]) and (destination in data["Area No"]): 
                rides = Ride.objects.all()
                if(len(rides) == 0):
                    count = 1
                else:
                    count = 1 + rides[len(rides)-1].ride_id
                request.data["ride_id"] = count
                request.data["timestamp"] = string_convert(request.data["timestamp"])        
                r=requests.post("http://127.0.0.1:8000/api/v1/db/write",json={"table":"Ride","insert":request.data})
                json_data = {"username":request.data['created_by'], "ride_id":count}
                r2=requests.post("http://127.0.0.1:8000/api/v1/db/write",json={"table":"User_rides","insert":json_data})
                if (r.status_code==200 and r2.status_code==200):
                    return Response({"count": count},status=status.HTTP_201_CREATED)
                else:
                    return Response({},status=status.HTTP_400_BAD_REQUEST)
            else:
                    return Response({},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class rideDetails(APIView):
    def get(self,request,ride,format=None):
        ride_ = Ride.objects.filter(ride_id=ride)
        if len(ride_)==0:
            return Response({},status=status.HTTP_204_NO_CONTENT)
        else:
            ride_=[i.__dict__ for i in ride_][0]
            # print(ride_)
            user_list = User_rides.objects.filter(ride_id_id=ride)
            user_list=[i.__dict__["username_id"] for i in user_list]
            user_list.remove(ride_["created_by_id"])
            # print(user_list)
            x = {"ride_id":ride_["ride_id"],"created_by":ride_["created_by_id"],"users":user_list
            , "source":ride_["source"],"destination":ride_["destination"],"timestamp":ride_["timestamp"]}
            return Response(x,status=status.HTTP_200_OK)
    def delete(self,request,ride,format=None):
        ride_ = Ride.objects.filter(ride_id=ride)
        if len(ride_)==0:
            return Response({},status=status.HTTP_204_NO_CONTENT)
        else:
            ride_.delete()
            return Response({},status=status.HTTP_200_OK)

class user_ridesList(APIView):
    def get(self, request):
        user_rides = User_rides.objects.all()
        serializer = User_rideSerializer(user_rides, many = True)
        return Response(serializer.data)
    def post(self, request, ride):
        ride_id = ride
        username = request.data['username']
        json_data = {"username":username, "ride_id":ride_id}
        r1=requests.post("http://127.0.0.1:8000/api/v1/db/write",json={"table":"User_rides","insert":json_data})
        if (r1.status_code==200 ):
            return Response({},status=status.HTTP_201_CREATED)
        else:
            return Response({},status=status.HTTP_400_BAD_REQUEST)


class table_list(APIView):
    def post(self, request):
        table = request.data["table"]
        columns = ", ".join(request.data["columns"])
        where = request.data["where"].split("=")
        where = where[0]+" = '"+ where[1] +"';"
        query = "SELECT "+ columns +" FROM "+ "rideshare_"+table + " WHERE " + where
        if(table == "User"):
            users = User.objects.raw(query)
            serializer = UserSerializer(users, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        elif(table == "Ride"):
            rides = Ride.objects.raw(query)
            serializer = RideSerializer(rides, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        elif(table == "User_rides"):
            user_rides = User_rides.objects.raw(query)
            serializer = User_rideSerializer(user_rides, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

class table_write(APIView):
    def post(self, request):
        print(request.data)
        table = request.data["table"]
        if(table == "User"):
            serializer = UserSerializer(data = request.data["insert"])
            if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status = status.HTTP_200_OK)
        elif(table == "Ride"):
            serializer = RideSerializer(data = request.data["insert"])
            if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status = status.HTTP_200_OK)
            print(serializer.validated_data)
            
        elif(table == "User_rides"):
            serializer = User_rideSerializer(data = request.data["insert"])
            if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status = status.HTTP_200_OK)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def displayRideDetails(request):
    return HttpResponse(request.GET["source"])