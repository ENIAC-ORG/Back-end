from django.urls import path 
from .views import RecomendationSysView


urlpatterns = [
    path('patient_recomend/' , RecomendationSysView.as_view({'post' : 'get_recomended_doctors'}) , name='recomended_doctors') , 
    path('doctor_form/' , RecomendationSysView.as_view({'post' : 'doctor_info_api'}) , name='doctor_info') , 
]
