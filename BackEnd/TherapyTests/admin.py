from django.contrib import admin
from .models import TherapyTests , GlasserTest , MedicalRecord , TreatementHistory , MedicalRecordPermission 
admin.site.register(TherapyTests)
admin.site.register(GlasserTest)
admin.site.register(MedicalRecord)
admin.site.register(TreatementHistory)
admin.site.register(MedicalRecordPermission)

# Register your models here.
