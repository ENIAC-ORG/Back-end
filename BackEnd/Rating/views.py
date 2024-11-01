from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import  RatingSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, transaction
from reservation.models import Reservation

class RatingViewSet(APIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]


    def post(self, request):
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            pationt_id = request.user.id
            psychiatrist = serializer.validated_data['psychiatrist']

            try:
                pationt = Pationt.objects.get(user_id=pationt_id)
            except Pationt.DoesNotExist:
                return Response({'error': 'Pationt not found.'}, status=status.HTTP_404_NOT_FOUND)

            if Rating.objects.filter(pationt=pationt, psychiatrist=psychiatrist).exists():
                return Response({'error': 'You have already rated this psychiatrist.'}, status=status.HTTP_400_BAD_REQUEST)
                
            if not Reservation.objects.filter(pationt=pationt, psychiatrist=psychiatrist).exists():
                return Response({'error': 'You can only rate a psychiatrist if you have had a reservation with them.'}, status=status.HTTP_400_BAD_REQUEST)

                
            doctor_rate = Rating.objects.create(
                        psychiatrist=psychiatrist,
                        pationt=pationt,
                        rating=serializer.validated_data['rating'],
                        comments=serializer.validated_data['comments'],
                    )
            doctor_rate.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("hellllllllllllllllllllllllllllllllllllllllllllllllllllll")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)