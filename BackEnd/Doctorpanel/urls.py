from django.urls import path
from .views import *

urlpatterns = [
    path("get_rating/", DoctorPanelView.as_view({'get': 'get_rating'}), name="GetRating"),
    path("ThisWeekResevations/", DoctorPanelView.as_view({'get': 'ThisWeekResevations'}), name="ThisWeekReservations"),
    path("NextWeekReservations/", DoctorPanelView.as_view({'get': 'NextWeekReservations'}), name="NextWeekReservations"),
    path('doctor/get-free-times/', DoctorPanelView.as_view({'get': 'GetFreeTimes'}), name="GetFreeTimes"),
    path('doctor/post-free-times/', DoctorPanelView.as_view({'post': 'PostFreeTimes'}), name="PostFreeTimes"),
    path('doctor/update-free-times/', DoctorPanelView.as_view({'put': 'UpdateFreeTimes'}), name="UpdateFreeTimes"),
    path('doctor/delete-free-times/', DoctorPanelView.as_view({'post': 'DeleteFreeTimes'}), name="DeleteFreeTimes"),
    path('doctor/update-free-time-by-date/', DoctorPanelView.as_view({'put': 'UpdateFreeTimeByDate'}), name="UpdateFreeTimeByDate"),
    path('pending_doctor/accept/<int:pk>/', AdminDoctorPannel.as_view({'post': 'accept'}), name="AcceptPendingDoctor"),
    path('pending_doctor/deny/<int:pk>/', AdminDoctorPannel.as_view({'post': 'deny'}), name="DenyPendingDoctor"),
    path('pending_doctor/', AdminDoctorPannel.as_view({'get': 'get_queryset'}), name="PendingDoctorsList"),
    path('compeletedoctorinfo/', PsychiatristInfoView.as_view({'post': 'PostDoctorInfo'}), name="CompleteDoctorInfo"),
    path('getdoctorinfo/<int:pk>/', PsychiatristInfoView.as_view({'get': 'GetDoctorInfo'}), name="GetDoctorInfo"),
]

    #  requesting query : http://localhost:8000/doctorpannel/pending_doctor/search=zahra alizaeh?
    #  requesting query : http://localhost:8000/doctorpannel/pending_doctor/search=1234555? --> using doctor code 

