from django.urls import path
from .views import RatingViewSet

urlpatterns = [
    path('Rate/', RatingViewSet.as_view(), name='Rate'),
    path('get/<int:pk>/', RatingViewSet.as_view(), name='GetRate'),
]
