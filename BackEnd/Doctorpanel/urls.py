from django.urls import path
from .views import *

urlpatterns = [
    path("get_rating/" , DoctorPanelView.as_view({'get':'get_rating'}) , name="GetRating") , 
    path("ThisWeekResevations/" , DoctorPanelView.as_view({'get':'ThisWeekResevations'}) , name="ReservationList") , 
    path("NextWeekReservations/" , DoctorPanelView.as_view({'get':'NextWeekReservations'}) , name="ReservationList2") , 
    path('doctor/post-free-time/', DoctorPanelView.as_view({'post':'PostFreeTime'})),
    # path('doctor/update-free-time/', DoctorPanelView.as_view({'put':'UpdateFreeTime'})),
    path('doctor/delete-free-time/', DoctorPanelView.as_view({'post':'DeleteFreeTime'})),

]
