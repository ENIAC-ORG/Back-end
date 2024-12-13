from django.urls import path
from .views import *

urlpatterns = [
    path("get_rating/" , DoctorPanelView.as_view({'get':'get_rating'}) , name="GetRating") , 
    path("ThisWeekResevations/" , DoctorPanelView.as_view({'get':'ThisWeekResevations'}) , name="ReservationList") , 
    path("NextWeekReservations/" , DoctorPanelView.as_view({'get':'NextWeekReservations'}) , name="ReservationList2") , 
    path('doctor/get-free-times/', DoctorPanelView.as_view({'get':'GetFreeTimes'})),
    path('doctor/post-free-times/', DoctorPanelView.as_view({'post':'PostFreeTimes'})),
    path('doctor/update-free-times/', DoctorPanelView.as_view({'put':'UpdateFreeTimes'})),
    path('doctor/delete-free-times/', DoctorPanelView.as_view({'post':'DeleteFreeTimes'})),
    path('doctor/update-free-time-by-date/', DoctorPanelView.as_view({'put':'UpdateFreeTimeByDate'})),
    path('pending_doctor/accept/<int:pk>/' , AdminDoctorPannel.as_view({'post': 'accept' })) , 
    path('pending_doctor/deny/<int:pk>/' , AdminDoctorPannel.as_view({'post': 'deny'})) , 
    path('pending_doctor/' , AdminDoctorPannel.as_view({'get' : 'get_queryset'})) , 
    path('compeletedoctorinfo/',PsychiatristInfoView.as_view({'post':'PostDoctorInfo'})),
    path('getdoctorinfo/<int:pk>/',PsychiatristInfoView.as_view({'get':'GetDoctorInfo'})),
    #  requesting query : http://localhost:8000/doctorpannel/pending_doctor/search=zahra alizaeh?
    #  requesting query : http://localhost:8000/doctorpannel/pending_doctor/search=1234555? --> using doctor code 
]