from django.db import models
from django.conf import settings

class PatientFormResponse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_form")
    age = models.IntegerField()
    symptoms = models.JSONField()  # لیستی از علائم
    preferred_therapy_methods = models.JSONField(blank=True, null=True)
    presentation_preference = models.CharField(max_length=50, choices=[("حضوری", "حضوری"), ("مجازی", "مجازی"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])
    communication_preference = models.JSONField(blank=True, null=True)
    therapist_gender_preference = models.CharField(max_length=50, choices=[("زن", "زن"), ("مرد", "مرد"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])
    religion_preference = models.CharField(max_length=50, choices=[("مذهبی", "مذهبی"), ("غیرمذهبی", "غیرمذهبی"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])
    treatment_duration = models.CharField(max_length=50, choices=[("کوتاه‌مدت", "کوتاه‌مدت"), ("بلندمدت", "بلندمدت")])
    stress_level = models.IntegerField()
    current_medications = models.TextField(blank=True, null=True)
    past_treatments = models.TextField(blank=True, null=True)
    suicidal_thoughts = models.CharField(max_length=50, choices=[("هرگز", "هرگز"), ("یک ماه پیش", "یک ماه پیش"), ("هفته گذشته", "هفته گذشته"), ("همین حالا", "همین حالا")])
    physical_issues = models.TextField(blank=True, null=True)
    sleep_hours = models.IntegerField(blank=True, null=True)
    energy_level = models.CharField(max_length=50, choices=[("کم", "کم"), ("متوسط", "متوسط"), ("زیاد", "زیاد")])
    social_activities = models.BooleanField(default=False)
    expectations = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Patient Form - {self.user.email}"

class PsychologistFormResponse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="psychologist_form")
    specialties = models.JSONField()
    therapy_methods = models.JSONField()
    age_groups = models.JSONField()
    session_preference = models.CharField(max_length=50, choices=[("حضوری", "حضوری"), ("مجازی", "مجازی"), ("هر دو", "هر دو")])
    communication_preference = models.JSONField(blank=True, null=True)
    religion = models.CharField(max_length=50, choices=[("مذهبی", "مذهبی"), ("غیرمذهبی", "غیرمذهبی"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])
    gender = models.CharField(max_length=50, choices=[("زن", "زن"), ("مرد", "مرد"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])
    experience_years = models.IntegerField()
    max_sessions_per_week = models.IntegerField(blank=True, null=True)
    prefers_religious_patients = models.CharField(max_length=50, choices=[("مذهبی", "مذهبی"), ("غیرمذهبی", "غیرمذهبی"), ("فرقی نمی‌کند", "فرقی نمی‌کند")], blank=True, null=True)
    prefers_gender = models.CharField(max_length=50, choices=[("زن", "زن"), ("مرد", "مرد"), ("فرقی نمی‌کند", "فرقی نمی‌کند")], blank=True, null=True)
    physical_conditions_experience = models.BooleanField(default=False)
    crisis_management = models.BooleanField(default=False)
    additional_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Psychologist Form - {self.user.email}"
