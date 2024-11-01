from django.urls import path
from .views import RatingViewSet

urlpatterns = [
    path('Rate/', RatingViewSet.as_view(), name='Rate'),
]
