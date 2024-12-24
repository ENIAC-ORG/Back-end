from django.urls import path
from .views import (
    PatientFormAPIView,
    PsychologistFormAPIView,
    MatchPatientToPsychologistsAPIView
)

urlpatterns = [
    # API برای مدیریت فرم بیمار
    path('patient/form/', PatientFormAPIView.as_view(), name='patient_form'),

    # API برای مدیریت فرم روانشناس
    path('psychologist/form/', PsychologistFormAPIView.as_view(), name='psychologist_form'),

    # API برای پیدا کردن روانشناسان مناسب برای بیمار
    path('match/patient-to-psychologists/', MatchPatientToPsychologistsAPIView.as_view(), name='match_patient_to_psychologists'),
]
