from django.urls import path
from .views import *

urlpatterns = [
    path("create/" , ReservationView.as_view({'post':'create'}) , name="create") , 
    path("delete/<int:pk>/" , ReservationView.as_view({'delete': 'destroy'}) , name="delete") , 
    path('get-free-time/<int:pk>/', ReservationView.as_view({'get':'GetAllFreeTime'})),
    path("between_dates/", ReservationView.as_view({'post': 'between_dates'}), name="between_dates"),
    path("last_month/" ,ReservationView.as_view({'post' : 'list_month'}),name="last_month" ),
    path("last_week/" , ReservationView.as_view({'post' : 'last_week'}) , name="last_week"),
    path('feedback/<int:reservation_id>/', FeedbackAPIView.as_view(), name='api_feedback'),
]
