
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from counseling.models import Psychiatrist,Pationt
from .serializers import DoctorCountSerializer, PationtCountSerializer,ReservationCountSerializer
from reservation.models import Reservation

# class DoctorCountView(APIView):
#     def get(self, request):
#         doctor_count = Psychiatrist.objects.count()
#         serializer = DoctorCountSerializer({'doctor_count': doctor_count})
#         return Response(serializer.data, status=status.HTTP_200_OK)

# class PationtCountView(APIView):
#     def get(self, request):
#         Pationt_count = Pationt.objects.count()
#         serializer = PationtCountSerializer({'Pationt_count': Pationt_count})
#         return Response(serializer.data, status=status.HTTP_200_OK)


class CountView(APIView):
    def get(self, request):
        doctor_count = Psychiatrist.objects.count()
        Pationt_count = Pationt.objects.count()
        reservation_count=Reservation.objects.count()

        doctor_serializer = DoctorCountSerializer({'doctor_count': doctor_count})
        Pationt_serializer = PationtCountSerializer({'Pationt_count': Pationt_count})
        reservation_serializer = ReservationCountSerializer({'reservation_count': reservation_count})
        data = {
            'doctor_data': doctor_serializer.data,
            'Pationt_data': Pationt_serializer.data,
            'reservation_data' :reservation_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)