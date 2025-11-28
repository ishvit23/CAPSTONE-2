from django.urls import path
from .views import ChatbotView, ChatHistoryView
from .auth_views import (
    GoogleAuthInitView,
    GoogleAuthCallbackView,
    CurrentUserView,
)

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chat'),
    path('chat/history/', ChatHistoryView.as_view(), name='chat-history'),
    path('auth/google/login/', GoogleAuthInitView.as_view(), name='google-login'),
    path('auth/google/callback/', GoogleAuthCallbackView.as_view(), name='google-callback'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
] 