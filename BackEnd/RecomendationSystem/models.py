from django.db import models
from django.conf import settings

class PatientFormResponse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_form")

    # اطلاعات اولیه و وضعیت فردی
    age = models.IntegerField()  # سن
    energy_level = models.CharField(max_length=50, choices=[("کم", "کم"), ("متوسط", "متوسط"), ("زیاد", "زیاد")])  # سطح انرژی
    current_medications = models.TextField(blank=True, null=True)  # داروهای مصرفی
    physical_issues = models.TextField(blank=True, null=True)  # مشکلات جسمی
    symptoms = models.JSONField()  # علائم

    # سابقه درمانی و وضعیت روانی
    past_treatments = models.TextField(blank=True, null=True)  # درمان‌های قبلی
    suicidal_thoughts = models.CharField(max_length=50, choices=[("هرگز", "هرگز"), ("یک ماه پیش", "یک ماه پیش"), ("هفته گذشته", "هفته گذشته"), ("همین حالا", "همین حالا")])  # افکار خودکشی

    # حالات روحی و اجتماعی
    stress_level = models.IntegerField()  # سطح استرس روزانه
    sleep_hours = models.IntegerField(blank=True, null=True)  # ساعات خواب
    social_activities = models.BooleanField(default=False)  # فعالیت‌های اجتماعی
     # حمایت عاطفی بیمار
    support_system = models.CharField(max_length=50, choices=[("کم", "کم"), ("متوسط", "متوسط"), ("زیاد", "زیاد")],help_text="سطح حمایت اجتماعی و عاطفی بیمار"
    ,null=True)
    # انتظارات و ترجیحات درمانی
    treatment_duration = models.CharField(max_length=50, choices=[("کوتاه‌مدت", "کوتاه‌مدت"), ("بلندمدت", "بلندمدت")])  # مدت زمان درمان
    religion_preference = models.CharField(max_length=50, choices=[("مذهبی", "مذهبی"), ("غیرمذهبی", "غیرمذهبی"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])  # ترجیح مذهبی
    therapist_gender_preference = models.CharField(max_length=50, choices=[("زن", "زن"), ("مرد", "مرد"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])  # ترجیح جنسیت درمانگر
    presentation_preference = models.CharField(max_length=50, choices=[("حضوری", "حضوری"), ("مجازی", "مجازی"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])  # ترجیح نوع جلسات
    preferred_therapy_methods = models.JSONField(blank=True, null=True)  # روش‌های درمانی مورد نظر
    communication_preference = models.JSONField(blank=True, null=True)  # روش‌های ارتباط با درمانگر
    expectations = models.TextField(blank=True, null=True)  # انتظارات از درمانگر

    # اطلاعات اضافی
    additional_notes = models.TextField(blank=True, null=True)  # توضیحات اضافی

    def __str__(self):
        return f"Patient Form - {self.user.email}"

class PsychologistFormResponse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="psychologist_form")
    
    specialties = models.JSONField()  # تخصص‌ها
    therapy_methods = models.JSONField()  # روش‌های درمانی
    age_groups = models.JSONField()  # گروه‌های سنی
    
    session_preference = models.CharField(max_length=50, choices=[("حضوری", "حضوری"), ("مجازی", "مجازی"), ("هر دو", "هر دو")])  # نوع جلسات
    communication_preference = models.JSONField(blank=True, null=True)  # روش‌های ارتباطی
    
    religion = models.CharField(max_length=50, choices=[("مذهبی", "مذهبی"), ("غیرمذهبی", "غیرمذهبی"), ("فرقی نمی‌کند", "فرقی نمی‌کند")])  # مذهبی یا غیرمذهبی بودن
    gender = models.CharField(max_length=50, choices=[("زن", "زن"), ("مرد", "مرد")])  # جنسیت
    
    experience_years = models.IntegerField()  # سابقه کاری
    max_sessions_per_week = models.IntegerField(blank=True, null=True)  # حداکثر تعداد جلسات
    treatment_duration = models.CharField(max_length=50, choices=[("کوتاه‌مدت", "کوتاه‌مدت"), ("بلندمدت", "بلندمدت")])  # مدت زمان درمان

    prefers_religious_patients = models.CharField(max_length=50, choices=[("مذهبی", "مذهبی"), ("غیرمذهبی", "غیرمذهبی"), ("فرقی نمی‌کند", "فرقی نمی‌کند")], blank=True, null=True)  # ترجیح مذهبی بیماران
    prefers_gender = models.CharField(max_length=50, choices=[("زن", "زن"), ("مرد", "مرد"), ("فرقی نمی‌کند", "فرقی نمی‌کند")], blank=True, null=True)  # ترجیح جنسیت بیمار
    
    physical_conditions_experience = models.BooleanField(default=False)  # تجربه کار با بیماران دارای مشکلات جسمی
    crisis_management = models.BooleanField(default=False)  # تجربه مدیریت بحران
    medications_experience = models.BooleanField(default=False) # تجربه دارو خاص

    additional_notes = models.TextField(blank=True, null=True)  # توضیحات اضافی

    def __str__(self):
        return f"Psychologist Form - {self.user.email}"

