from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepressionChatView,ProcessWavVoiceView


# Define custom URLs for the additional methods
urlpatterns = [
    path('chat/create/', DepressionChatView.as_view({'post': 'create_new_conversation'}), name='create_new_conversation'),
    path('chat/<int:pk>/message/', DepressionChatView.as_view({'post': 'Message'}), name='send_message'),
    path('chat/<int:pk>/', DepressionChatView.as_view({'get': 'Retrieve_conversation'}), name='retrieve_conversation'),
    path('chat/all/', DepressionChatView.as_view({'get': 'Retrieve_all_conversations'}), name='retrieve_all_conversations'),
    path('chat/<int:pk>/delete/', DepressionChatView.as_view({'delete': 'delete'}), name='delete_conversation'),
    path('process_wav_voice/', ProcessWavVoiceView.as_view(), name='process_wav_voice'),
]

