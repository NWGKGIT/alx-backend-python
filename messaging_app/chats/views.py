# chats/views.py

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter

class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for conversations.
    """
    serializer_class = ConversationSerializer
    # Combine IsAuthenticated with our custom permission
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['messages__message_body'] 

    def get_queryset(self):
        # Ensure users only see their own conversations
        return self.request.user.conversations.all()

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for messages.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    
    # Add Filter Backend and the specific FilterSet class
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MessageFilter
    ordering_fields = ['sent_at']

    def get_queryset(self):
        user = self.request.user
        # Ensure users only see messages from conversations they participate in
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)