from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.RoomListCreateView.as_view(), name='room_list_create'),  # لیست و ایجاد گروه
    path('rooms/<int:room_id>/messages/', views.MessageListCreateView.as_view(), name='message_list_create'),  # لیست و ارسال پیام
    path('messages/<int:message_id>/', views.DeleteMessageView.as_view(), name='delete_message'),  # حذف پیام
    path('rooms/<int:room_id>/', views.DeleteRoomView.as_view(), name='delete_room'),  # حذف گروه
    path('rooms/<int:room_id>/update/', views.UpdateRoomView.as_view(), name='update_room'),  # ویرایش گروه
    path('rooms/<int:room_id>/toggle-visibility/', views.ToggleRoomVisibilityView.as_view(), name='toggle_room_visibility'),  # مخفی کردن گروه
]
