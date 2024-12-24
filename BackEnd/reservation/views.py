import calendar
from django.shortcuts import render
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status 
from counseling.models import Pationt , Psychiatrist 
from .serializer import *
from .models import Reservation
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import date , timedelta
from Doctorpanel.models import FreeTime
from django.db import transaction
from datetime import date , timedelta ,datetime
from Doctorpanel.serializers import FreeTimeSerializer , GETFreeTimeSerializer


class ReservationView(viewsets.ModelViewSet ) : 
    """
    A viewset for reservation that provides `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReserveSerializer 
    queryset = Reservation.objects.all()
    def create(self, request, *args, **kwargs):
        serializer = CreateReserveSerializer(data= request.data )
        serializer.is_valid(raise_exception=True)
        validated_data =  serializer.validated_data
        
        if not hasattr(request, 'user'):
            return Response({'message': 'user is not loged in'}, status=status.HTTP_400_BAD_REQUEST)
        id = validated_data['doctor_id']
        doctor =  Psychiatrist.objects.filter(id = id )
        if not doctor.exists() : 
            return Response({'message': 'docotr id is not corroct.'}, status=status.HTTP_400_BAD_REQUEST)

        chosen_date = validated_data["date"]
        chosen_time = validated_data["time"]
        free_time = FreeTime.objects.filter(psychiatrist=doctor.first(), date=str(chosen_date), time=str(chosen_time)).first()
        if not free_time:
            return Response({'message': 'This time is not available for the chosen doctor.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.role=='doctor':
            return Response({'Message':'The role must be paitient'})
        pationt = Pationt.objects.filter( user = request.user ).first()
        # if not pationt.exists():
        #     return Response({'Message':'This paitient dose not  exist'})
        last_reservation = Reservation.objects.filter(pationt = pationt )
        
        if last_reservation.exists() : 
            last_reservation = last_reservation.last()
            # parsed_date = datetime.strptime(validated_data["date"], "%Y-%m-%d")
            diff = validated_data["date"] - last_reservation.date if validated_data["date"] > last_reservation.date  else last_reservation.date - validated_data["date"] 
            print( "diffffffffffffffff *****************" , diff )
            if diff.days < 8: 
                return Response( {"message" : "you can not reservere 2 times under 8 days drift"} , status=status.HTTP_400_BAD_REQUEST)

        reserve = Reservation.objects.create(
                type = validated_data["type"] , 
                date = chosen_date, 
                time = chosen_time , 
                psychiatrist = doctor.first() ,
                day = free_time.day,
                pationt = pationt
            )
        free_time.delete()

        response = {
                "reserve" : ReserveSerializer(reserve).data ,
                "message" : "reservation successfully created"
            }
            
        return Response( data=response , status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            reservation_id = kwargs.get('pk')
            reservation = Reservation.objects.get(id=reservation_id)
            doctor = reservation.psychiatrist
            reserved_date = reservation.date
            reserved_time = reservation.time
            reserved_day=reservation.day
            reserved_month = calendar.month_name[reservation.date.month]
            
            with transaction.atomic():
                reservation.delete()
                FreeTime.objects.create(psychiatrist=doctor,date=reserved_date,day=reserved_day,month=reserved_month,time=reserved_time)
                
            return Response({"message": "Reservation successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Reservation.DoesNotExist:
            return Response({"message": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)

    def GetAllFreeTime(self, request, *args, **kwargs):
        try:
            psychiatrist_id = kwargs.get('pk')
            psychiatrist = Psychiatrist.objects.get(id=psychiatrist_id)
        except Psychiatrist.DoesNotExist:
            return Response({'error': 'Psychiatrist not found.'}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()
        end_date = today + timedelta(days=30)

        free_times = FreeTime.objects.filter(
            psychiatrist=psychiatrist,
            date__range=[today, end_date]
        ).order_by('date', 'time')

        serializer = GETFreeTimeSerializer(free_times, many=True)
        return Response({'Free Time List': serializer.data}, status=status.HTTP_200_OK)


    def list_month(self, request):
        queryset = Reservation.objects.all()
        month = request.data.get('month')
        year = request.data.get('year')
        docotor_id = request.data.get('doctor_id')
        docotor = Psychiatrist.objects.filter( id = docotor_id)
        if not docotor.exists() : 
            return Response({"message" : 'there is not doctor with this id '} , status=status.HTTP_400_BAD_REQUEST)
        docotor = docotor.first()
        queryset = queryset.filter(date__year=year, date__month=month , psychiatrist = docotor)
        # print("here*******************************************************")
        serializer = ReserveSerializer(queryset, many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)
    
    def last_week( self , request ) : 
        # get the date of saturday 
        # day_dict = {
        #     0 : 'شنبه' , 
        #     1 : 'یکشنبه',
        #     2 : 'دوشنبه' , 
        #     3 : 'سه شنبه'  , 
        #     4 : 'چهارشنبه' , 
        #     5 : 'پنج‌شنبه' , 
        #     6 : 'جمعه'  
        # }

        serializer = DaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        date1 = serializer.validated_data['date']
        doctor = serializer.validated_data['doctor_id']
        day = (date1.weekday() + 4 )%7 
        saturday = date( day= date1.day  , month=date1.month , year=date1.year) - timedelta(days=day ) 
        thirsday = date( day= saturday.day , month=saturday.month , year=saturday.year) + timedelta(days=5)
        
        reservations = Reservation.objects.filter( psychiatrist = doctor)
        print(reservations )
        reservations = reservations.filter(date__range=[str(saturday) , str(thirsday) ])
        print([str(saturday) , str(thirsday) ])
        serializer = ReserveSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def between_dates(self, request):
        serializer = BetweenDatesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        doctor_id = serializer.validated_data['doctor_id']

        try:
            doctor = Psychiatrist.objects.get(id=doctor_id)
        except ObjectDoesNotExist:
            return Response({"message": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        if not start_date or not end_date:
            return Response({"message": "Both start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            start_date = timezone.datetime.strptime( str(start_date) , "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime( str(end_date), "%Y-%m-%d").date()
        except ValueError:
            return Response({"message": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        reservations = Reservation.objects.filter(date__range=[start_date, end_date], psychiatrist=doctor)
        serializer = ReserveSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    










from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Reservation

class FeedbackAPIView(APIView):

    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        feedback = request.data.get('feedback')

        if feedback:
            reservation.feedback = feedback
            reservation.save()
            return Response({'message': 'فیدبک با موفقیت ثبت شد.'}, status=status.HTTP_200_OK)

        return Response({'error': 'فیدبک ارسال نشده است.'}, status=status.HTTP_400_BAD_REQUEST)
