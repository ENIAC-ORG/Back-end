from django.contrib import admin
from .models import ConMessage , Conversation
# Register your models here.
admin.site.register(Conversation)
admin.site.register(ConMessage)