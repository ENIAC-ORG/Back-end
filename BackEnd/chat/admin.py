from django.contrib import admin
from .models import Message , RoomMembership  , Room
admin.site.register( Message )
admin.site.register(RoomMembership )
admin.site.register(Room )
