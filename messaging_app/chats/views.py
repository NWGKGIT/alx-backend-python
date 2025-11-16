# messaging_app/chats/views.py

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    # Check for 'filters'
    filter_backends = [filters.SearchFilter]
    search_fields = ['messages__message_body'] # Example filter

    def get_queryset(self):
        return self.request.user.conversations.all()

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    # Check for 'filters'
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sent_at']

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        # Override create to use 'status' code explicitly
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Check for 'status'
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)