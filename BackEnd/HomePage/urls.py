from .views import *
from django.urls import path


urlpatterns = [
    # path('PationtCount/' , PationtCountView.as_view() , name='PationtCount' ) ,
    # path('DoctorCount/' , DoctorCountView.as_view() , name='DoctorCount' ) ,
    path('count/',CountView.as_view(),name='count'),


]


#fffffffffffffffffffffffffffffff