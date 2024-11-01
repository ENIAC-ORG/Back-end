import calendar
from django.shortcuts import render
from rest_framework import viewsets
from reservation import views
from rest_framework.views import APIView
from rest_framework.response import Response
from counseling.models import  Psychiatrist
from reservation.models import Reservation
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Rating.views import RatingViewSet
from Rating.models import Rating
from django.db.models import Count, Avg
from .serializers import DoctorPanelSerializer ,ReservationListSerializer , FreeTimeSerializer
from datetime import datetime, timedelta
from .models import FreeTime
from rest_framework import generics, status
from rest_framework.status import HTTP_404_NOT_FOUND
from datetime import datetime, time
from rest_framework.permissions import IsAuthenticated

class DoctorPanelView(viewsets.ModelViewSet):
    serializer_class=FreeTimeSerializer
    permission_classes = [IsAuthenticated]
    queryset = FreeTime.objects.all()
    def get_rating(self, request):
        # serializer = DoctorPanelSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # psychiatrist_id=serializer.validated_data['psychiatrist_id']
        try:
            psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
        except Psychiatrist.DoesNotExist:
            return Response({'error': 'Psychiatrist not found.'}, status=HTTP_404_NOT_FOUND)
        ratings = Rating.objects.filter(psychiatrist=psychiatrist)

        ratings_count = ratings.values('rating').annotate(count=Count('rating'))

        average_score = ratings.aggregate(average=Avg('rating'))['average']

        total_ratings_count = ratings.count()

        response_data = {
            'ratings_count': {choice[1]: 0 for choice in Rating.CHOICES},
            'average_score': average_score or 0,
            'total_ratings_count': total_ratings_count
        }

        # Update response data with actual ratings count
        for rating_count in ratings_count:
            response_data['ratings_count'][Rating.CHOICES[rating_count['rating'] - 1][1]] = rating_count['count']

        return Response(response_data)
    
    def ThisWeekResevations(self,request):
        #for each date it shows the rervations from saturday to friday 
        # serializer = DoctorPanelSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # psychiatrist_id=request.data.get('psychiatrist_id')
        try:
            psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
        except Psychiatrist.DoesNotExist:
            return Response({'error': 'Psychiatrist not found.'}, status=HTTP_404_NOT_FOUND)
        today = timezone.now().date()
        days_to_saturday = (today.weekday() - 5) % 7
        start_of_week = today - timedelta(days=days_to_saturday)
        end_of_week = start_of_week + timedelta(days=6)
        reservations_this_week = Reservation.objects.filter(
            psychiatrist=psychiatrist,
            date__range=[start_of_week, end_of_week]
        ).order_by('date','time')
        reservation_serializer = ReservationListSerializer(reservations_this_week, many=True)
        return Response({'reservations_this_week': reservation_serializer.data})


    def NextWeekReservations(self, request):
        #Reservation starting today to 7 days later 
        # serializer = DoctorPanelSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # psychiatrist_id = serializer.validated_data['psychiatrist_id']
        try:
            psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
        except Psychiatrist.DoesNotExist:
            return Response({'error': 'Psychiatrist not found.'}, status=HTTP_404_NOT_FOUND)
        today = timezone.now().date()
        end_date = today + timedelta(days=6)

        reservations_next_seven_days = Reservation.objects.filter(
            psychiatrist=psychiatrist,
            date__range=[today, end_date]
        ).order_by('date','time')
        reservation_serializer = ReservationListSerializer(reservations_next_seven_days, many=True)
        return Response({'reservations_next_seven_days': reservation_serializer.data})

    def PostFreeTime(self, request):
        serializer = FreeTimeSerializer(data=request.data)
        if serializer.is_valid():
            month = serializer.validated_data['month']
            day = serializer.validated_data['day']
            times = serializer.validated_data['time']

            if not times:
                return Response({'error': 'Times are required.'}, status=status.HTTP_400_BAD_REQUEST)

            times_list = list(set(time.strip() for time in times.split(',')))

            month_index = next(index for index, choice in enumerate(FreeTime.MONTH_CHOICES) if choice[0] == month) + 1

            year = datetime.now().year
            start_date = datetime(year, month_index, 1)
            end_date = start_date + timedelta(days=calendar.monthrange(year, month_index)[1] - 1)

            try:
                psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
            except Psychiatrist.DoesNotExist:
                return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)

            persian_to_weekday = {
                'شنبه': 5,    # Saturday
                'یکشنبه': 6,  # Sunday
                'دوشنبه': 0,  # Monday
                'سه‌شنبه': 1, # Tuesday
                'چهارشنبه': 2,# Wednesday
                'پنج‌شنبه': 3,# Thursday
                'جمعه': 4     # Friday
            }

            day_index = persian_to_weekday.get(day, None)
            if day_index is None:
                return Response({'error': 'Invalid day name.'}, status=status.HTTP_400_BAD_REQUEST)

            date = start_date
            while date.weekday() != day_index:
                date += timedelta(days=1)

            created_free_times = []
            while date <= end_date:
                for time in times_list:
                    conflicts = FreeTime.objects.filter(
                        psychiatrist=psychiatrist,
                        month=month,
                        day=day,
                        date=date,
                        time=time
                    ).exists()
                    if conflicts:
                        return Response({'error': f'Free time already exists for {day} at {time}.'}, status=status.HTTP_208_ALREADY_REPORTED)
                    else:
                        free_time = FreeTime.objects.create(
                            psychiatrist=psychiatrist,
                            month=month,
                            day=day,
                            date=date,
                            time=time
                        )
                        free_time.save()
                        created_free_times.append(free_time)

                date += timedelta(days=7)

            response_data = FreeTimeSerializer(created_free_times, many=True).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    # def UpdateFreeTime(self, request):
    #     serializer = FreeTimeSerializer(data=request.data)
    #     if serializer.is_valid():
    #         month = serializer.validated_data['month']
    #         day = serializer.validated_data['day']
    #         times = serializer.validated_data['time']

    #         if not times:
    #             return Response({'error': 'Times are required.'}, status=status.HTTP_400_BAD_REQUEST)

    #         times_list = list(set(time.strip() for time in times.split(',')))
    #         try:
    #             psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
    #         except Psychiatrist.DoesNotExist:
    #             return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)

    #         existing_free_times = FreeTime.objects.filter(
    #             psychiatrist=psychiatrist, month=month, day=day)

                            
            

    #         return Response(response_data, status=status.HTTP_200_OK)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
    def DeleteFreeTime(self, request):
        serializer = FreeTimeSerializer(data=request.data)
        if serializer.is_valid():
            month = serializer.validated_data['month']
            day = serializer.validated_data['day']
            times = serializer.validated_data['time']

            if not times:
                return Response({'error': 'Times are required.'}, status=status.HTTP_400_BAD_REQUEST)

            times_list = list(set(time.strip() for time in times.split(',')))

            try:
                psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
            except Psychiatrist.DoesNotExist:
                return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)

            not_found_times = []
            deleted_times = []

            for time in times_list:
                free_times = FreeTime.objects.filter(
                    psychiatrist=psychiatrist,
                    month=month,
                    day=day,
                    time=time
                )
                if free_times.exists():
                    free_times.delete()
                    deleted_times.append(time)
                else:
                    not_found_times.append(time)

            if not_found_times:
                return Response({
                    'error': 'Some free times were not found.',
                    'not_found_times': not_found_times,
                    'deleted_times': deleted_times
                }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'success': 'All specified free times deleted successfully.',
                    'deleted_times': deleted_times
                }, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    # def UpdateFreeTime(self, request):
    #     delete_response = self.DeleteFreeTime(request)
    #     if delete_response.status_code != status.HTTP_204_NO_CONTENT:
    #         return delete_response

    #     post_response = self.PostFreeTime(request)
    #     if post_response.status_code != status.HTTP_201_CREATED:
    #         return post_response

    #     return Response({'success': 'Free times updated successfully.'}, status=status.HTTP_200_OK)



        



            

        

