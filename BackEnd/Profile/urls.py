from django.urls import path
from .views import DoctorProfileViewSet

urlpatterns = [
    path('doctors/', DoctorProfileViewSet.as_view({'get': 'list', 'post': 'create'}), name='doctor-profiles-list'),
    path('doctors/<int:pk>/', DoctorProfileViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='doctor-profiles-detail'),
    path('doctors/typed/', DoctorProfileViewSet.as_view({'get': 'filter_by_profile_type'}), name='doctor-profiles-filter-by-profile-type'),
]
