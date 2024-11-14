from django.shortcuts import render, get_object_or_404
from .models import ChatRoom
from django.contrib.auth.decorators import login_required
from django.http import Http404

@login_required
def room_list(request):
    rooms = ChatRoom.objects.filter(owner=request.user)
    return render(request, 'chat/room_list.html', {
        'rooms': rooms
    })

@login_required
def room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)

    if room.owner != request.user:
        raise Http404("You do not have permission to access this room.")

    messages = room.messages.all()

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'messages': messages,
    })
