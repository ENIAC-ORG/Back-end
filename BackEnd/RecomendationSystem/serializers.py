from rest_framework import serializers
from .models import PatientFormResponse, PsychologistFormResponse

class PatientFormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientFormResponse
        fields = [
            'age', 'symptoms', 'preferred_therapy_methods', 'presentation_preference',
            'communication_preference', 'therapist_gender_preference',
            'religion_preference', 'treatment_duration', 'stress_level',
            'current_medications', 'past_treatments', 'suicidal_thoughts',
            'physical_issues', 'sleep_hours', 'energy_level',
            'social_activities', 'expectations', 'additional_notes'
        ]

class PsychologistFormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PsychologistFormResponse
        fields = [
            'specialties', 'therapy_methods', 'age_groups', 'session_preference',
            'communication_preference', 'religion', 'gender', 'experience_years',
            'max_sessions_per_week', 'prefers_religious_patients', 'prefers_gender',
            'physical_conditions_experience', 'crisis_management', 'additional_notes'
        ]
