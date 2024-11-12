from django.apps import AppConfig


class TherapytestsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "TherapyTests"

    def ready(self):
        import TherapyTests.signals
        
# /////////////////////