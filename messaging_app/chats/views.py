# messaging_app/chats/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return conversations the user is a participant in
        return self.request.user.conversations.all()

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return messages from conversations the user is in
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer):
        # Set the sender of the message to the authenticated user
        serializer.save(sender=self.request.user)