from rest_framework import serializers
from .models import PatientFormResponse,PsychologistFormResponse

class PatientFormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientFormResponse
        fields = [
            'age', 'symptoms', 'preferred_therapy_methods', 'presentation_preference',
            'communication_preference', 'therapist_gender_preference',
            'religion_preference', 'treatment_duration', 'stress_level',
            'current_medications', 'past_treatments', 'suicidal_thoughts',
            'physical_issues', 'sleep_hours', 'energy_level',
            'social_activities', 'support_system', 'expectations', 'additional_notes'
        ]

    def validate_symptoms(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Symptoms must be a list.")
        return value

    def validate_preferred_therapy_methods(self, value):
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Preferred therapy methods must be a list.")
        return value

    def validate_communication_preference(self, value):
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Communication preferences must be a list.")
        return value


class PsychologistFormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PsychologistFormResponse
        fields = [
            'specialties', 'therapy_methods', 'age_groups', 'session_preference',
            'communication_preference', 'religion', 'gender', 'experience_years',
            'max_sessions_per_week', 'treatment_duration', 'prefers_religious_patients',
            'prefers_gender', 'physical_conditions_experience', 'crisis_management',
            'medications_experience', 'additional_notes'
        ]

    def validate_specialties(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Specialties must be a list.")
        return value

    def validate_therapy_methods(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Therapy methods must be a list.")
        return value

    def validate_age_groups(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Age groups must be a list.")
        return value

    def validate_communication_preference(self, value):
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Communication preferences must be a list.")
        return value
