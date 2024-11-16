from django.urls import path
from .views import *

urlpatterns = [
    path("get_rating/" , DoctorPanelView.as_view({'get':'get_rating'}) , name="GetRating") , 
    path("ThisWeekResevations/" , DoctorPanelView.as_view({'get':'ThisWeekResevations'}) , name="ReservationList") , 
    path("NextWeekReservations/" , DoctorPanelView.as_view({'get':'NextWeekReservations'}) , name="ReservationList2") , 
    path('doctor/post-free-time/', DoctorPanelView.as_view({'post':'PostFreeTime'})),
    # path('doctor/update-free-time/', DoctorPanelView.as_view({'put':'UpdateFreeTime'})),
    path('doctor/delete-free-time/', DoctorPanelView.as_view({'post':'DeleteFreeTime'})),
    path('pending_doctor/<int:pk>/' , AdminDoctorPannel.as_view({'post': 'accept' , 'delete': 'deny'})) , 
    path('pending_doctor/' , AdminDoctorPannel.as_view({'get' : 'get_queryset'})) , 
    #  requesting query : http://localhost:8000/doctorpannel/pending_doctor/search=zahra alizaeh?
    #  requesting query : http://localhost:8000/doctorpannel/pending_doctor/search=1234555? --> using doctor code 
]
