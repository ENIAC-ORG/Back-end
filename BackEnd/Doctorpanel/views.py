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
from .serializers import  ReservationListSerializer , FreeTimeSerializer , GETFreeTimeSerializer , FreeTimeByDateSerializer ,DoctorInfoSerializer
from datetime import datetime, timedelta
from .models import FreeTime
from rest_framework import generics, status
from rest_framework.status import HTTP_404_NOT_FOUND
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import DoctorApplicationSerializer
from rest_framework import viewsets
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity  # For PostgreSQL databases
from accounts.models import Pending_doctor , User
import utils.email as email_handler 

class DoctorPanelView(viewsets.ModelViewSet):
    serializer_class=FreeTimeSerializer
    permission_classes = [IsAuthenticated]
    queryset = FreeTime.objects.all()
    def get_rating(self, request):
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

    def GetFreeTimes(self, request):
        try:
            psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
        except Psychiatrist.DoesNotExist:
            return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)

        current_time = timezone.now()

        free_times = FreeTime.objects.filter(
            psychiatrist=psychiatrist,
            date__gte=current_time.date()
        ).order_by('date', 'time')

        serializer = GETFreeTimeSerializer(free_times, many=True)
        return Response({'Free Time List': serializer.data}, status=status.HTTP_200_OK)

    def PostFreeTimes(self, request):
        serializer = FreeTimeSerializer(data=request.data)
        if serializer.is_valid():
            month = serializer.validated_data['month']
            day = serializer.validated_data['day']
            times = serializer.validated_data['time']            
            try:
                psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
            except Psychiatrist.DoesNotExist:
                return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            existing_free_times = FreeTime.objects.filter(
                psychiatrist=psychiatrist,
                month=month,
                day=day
                )       
            if existing_free_times.exists():
                return Response(
                {'error': 'Free times already exist for this date. Use UpdateFreeTime to modify existing times.'},
                status=status.HTTP_400_BAD_REQUEST
                )

            times_list = list(set(time.strip() for time in times.split(',')))

            created_free_times=self._create_free_times(month,day,times_list,psychiatrist)

            response_data = FreeTimeSerializer(created_free_times, many=True).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def DeleteFreeTimes(self, request):
        serializer = FreeTimeSerializer(data=request.data)
        if serializer.is_valid():
            month = serializer.validated_data['month']
            day = serializer.validated_data['day']
            times = serializer.validated_data['time']


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
                }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def UpdateFreeTimes(self, request):
        serializer = FreeTimeSerializer(data=request.data)
        if serializer.is_valid():
            month = serializer.validated_data['month']
            day = serializer.validated_data['day']
            times = serializer.validated_data['time']

            try:
                psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
            except Psychiatrist.DoesNotExist:
                return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            existing_free_times = FreeTime.objects.filter(
                psychiatrist=psychiatrist,
                month=month,
                day=day
                )
            if not existing_free_times.exists():
                return Response(
                    {'error': 'No free times exist for this date. Use PostFreeTime to add new free times.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            times_list = list(set(time.strip() for time in times.split(',')))

            FreeTime.objects.filter(
                psychiatrist=psychiatrist,
                month=month,
                day=day
            ).delete()

            created_free_times=self._create_free_times(month,day,times_list,psychiatrist)

            response_data = FreeTimeSerializer(created_free_times, many=True).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _create_free_times(self,month,day,times,psychiatrist):
        month_index = next(index for index, choice in enumerate(FreeTime.MONTH_CHOICES) if choice[0] == month) + 1
        current_year = datetime.now().year
        current_month = datetime.now().month
        if month_index < current_month:
            year = current_year + 1
        else:
            year = current_year
        start_date = datetime(year, month_index, 1)
        end_date = start_date + timedelta(days=calendar.monthrange(year, month_index)[1] - 1)

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
            for time in times :
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
        return created_free_times

    # def UpdateFreeTimeByDate(self, request):
    #     serializer = FreeTimeByDateSerializer(data=request.data)
    #     if serializer.is_valid():
    #         date = serializer.validated_data['date']
    #         newtime = serializer.validated_data['newtime']
    #         oldtime = serializer.validated_data['oldtime']

    #         try:
    #             psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
    #         except Psychiatrist.DoesNotExist:
    #             return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)
            
    #         existing_free_times = FreeTime.objects.filter(
    #             psychiatrist=psychiatrist,
    #             date=date,
    #             time=oldtime.strip()
    #             )
    #         if not existing_free_times.exists():
    #             return Response(
    #                 {'error': 'No free times exist for this date. Use PostFreeTime to add new free times.'},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
            
    #         updated_free_times = []
    #         for free_time in existing_free_times:
    #             free_time.time = newtime.strip()
    #             free_time.save()
    #             updated_free_times.append(free_time)
    #         response_data = FreeTimeSerializer(updated_free_times, many=True).data
    #         return Response(response_data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class PsychiatristInfoView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorInfoSerializer

    def PostDoctorInfo(self,request):
        try:
            psychiatrist = Psychiatrist.objects.get(user_id=request.user.id)
        except Psychiatrist.DoesNotExist:
            return Response({'error': 'Psychiatrist not found.'}, status=HTTP_404_NOT_FOUND)
        
        serializer = DoctorInfoSerializer(data = request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            field = serializer.validated_data['field']
            clinic_address = serializer.validated_data['clinic_address']
            clinic_telephone_number = serializer.validated_data['clinic_telephone_number']
            description = serializer.validated_data['description']
            psychiatrist.image = image
            psychiatrist.field = field
            psychiatrist.clinic_address=clinic_address
            psychiatrist.clinic_telephone_number = clinic_telephone_number
            psychiatrist.description = description
            psychiatrist.save()
            serializer = DoctorInfoSerializer(instance=psychiatrist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else : 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def GetDoctorInfo(self, request, *args, **kwargs):
        try:
            psychiatrist_id = kwargs.get('pk')
            psychiatrist = Psychiatrist.objects.get(id=psychiatrist_id)
        except Psychiatrist.DoesNotExist:
            return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorInfoSerializer(instance=psychiatrist)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminDoctorPannel(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Pending_doctor.objects.all()
    serializer_class = DoctorApplicationSerializer
    def get_queryset(self, request ):
        """
        Perform advanced search by combining firstname and lastname into a single field
        and applying similarity search on the combined name and doctorate_code.
        """
        queryset = Pending_doctor.objects.all()
        search_query = request.query_params.get('search', None)   #self.

        if search_query:
            # Combine firstname and lastname for similarity matching
            queryset = queryset.annotate(
                full_name=Concat('firstname', Value(' '), 'lastname', output_field=CharField())
            )
            # Apply similarity filtering
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) |
                Q(doctorate_code__icontains=search_query)
            ).annotate(
                name_similarity=TrigramSimilarity('full_name', search_query),
                code_similarity=TrigramSimilarity('doctorate_code', search_query)
            ).filter(
                Q(name_similarity__gte=0.3) | Q(code_similarity__gte=0.3)  # Adjust similarity threshold as needed
            ).order_by('-name_similarity', '-code_similarity')
        
        doctor_application_serializer = DoctorApplicationSerializer(queryset,many=True )
        return Response({"data" : doctor_application_serializer.data} , status= status.HTTP_200_OK)

    def accept(self , request, *args, **kwargs): 
        user = request.user
        if user.role != User.TYPE_ADMIN : 
            return Response({'message': 'Only ADMIN user can access this url.'}, status=status.HTTP_403_FORBIDDEN)
        u_id = kwargs.get('pk')
        doctors = Pending_doctor.objects.filter(id= u_id)
        
        if not doctors.exists(): 
            return Response({'message': 'There is not pending doctor with this id.'}, status=status.HTTP_400_BAD_REQUEST)
        try : 
            pending_doctor = doctors.first()
            user = pending_doctor.user
            psychiatrist = Psychiatrist.objects.create(
                user = user , 
                doctorate_code = pending_doctor.doctorate_code 
            )
            psychiatrist.save()
            pending_doctor.delete()
            # send email to doctor say the reason :)  
            subject =  'درخواست شما تایید شد . '
            email_handler.send_doctor_accept_email(
                subject=subject,
                recipient_list=[user.email],
                user=psychiatrist
            )

            return Response(
                {'message': 'Psychiatrist successfully created and pending doctor removed.'},
            status=status.HTTP_200_OK )
        
        except Exception as e:
            return Response(
                {'message': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def deny(self , request, *args, **kwargs): 
        
        user = request.user
        if user.role != User.TYPE_ADMIN : 
            return Response({'message': 'Only ADMIN user can access this url.'}, status=status.HTTP_403_FORBIDDEN)
        u_id = kwargs.get('pk')
        doctors = Pending_doctor.objects.filter(id= u_id)
        if not doctors.exists(): 
            return Response({'message': 'There is not pending doctor with this id.'}, status=status.HTTP_400_BAD_REQUEST)
        try : 
            pending_doctor = doctors.first()
            user = pending_doctor.user

            if pending_doctor.number_of_application == 0 : 
                pending_doctor.delete()
                user.delete()
                return Response(
                {'message': 'You have reached the number of allowed applicaton.you can not request an other time.'},
            status=status.HTTP_400_BAD_REQUEST )
            else : 
                message = request.data.get('message')
                # send email to pending use and say the reason of deny . 
                subject =  'درخواست شما رد شد . '
                email_handler.send_doctor_deny_email(
                subject=subject,
                recipient_list=[user.email],
                pending_user=pending_doctor,
                message=message
            )        
                pending_doctor.number_of_application -= 1 
                pending_doctor.save()
                return Response(
                    {'message': 'Ther is problem in the application of pending doctor.'},
                status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'message': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

        
