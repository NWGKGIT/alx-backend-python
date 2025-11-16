# messaging_app/chats/urls.py

from django.urls import path, include
# Import 'routers' from 'rest_framework'
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet

# Use 'routers.DefaultRouter()' per the check
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]