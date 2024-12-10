from .models import *
from .serializers import  RatingSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from reservation.models import Reservation
from django.db.models import Count, Avg

class RatingViewSet(APIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            psychiatrist_id = kwargs.get('pk')
            psychiatrist = Psychiatrist.objects.get(id=psychiatrist_id)
        except Psychiatrist.DoesNotExist:
            return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)

        ratings = Rating.objects.filter(psychiatrist=psychiatrist).select_related('pationt')
        # Compute statistics
        ratings_count = ratings.values('rating').annotate(count=Count('rating'))
        average_score = ratings.aggregate(average=Avg('rating'))['average']
        total_ratings_count = ratings.count()

        # Prepare the initial response data for statistics
        response_data = {
            'ratings_count': {choice[1]: 0 for choice in Rating.CHOICES},  # Initialize counts for all ratings
            'average_score': average_score or 0,  # Default to 0 if no ratings
            'total_ratings_count': total_ratings_count
        }

        # Update the response data with actual ratings count
        for rating_count in ratings_count:
            response_data['ratings_count'][Rating.CHOICES[rating_count['rating'] - 1][1]] = rating_count['count']

        # Add individual comments and ratings
        comments_data = [
            {
                "patient_name": rating.pationt.get_fullname(),  # Use the get_fullname method
                "rating": rating.rating,
                "comments": rating.comments
            }
            for rating in ratings
        ]

        # Combine statistics and comments into the final response
        response_data['comments'] = comments_data

        return Response(response_data, status=status.HTTP_200_OK)

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
                         date=now()
                    )
            doctor_rate.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)