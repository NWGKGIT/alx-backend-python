# messaging_app/chats/permissions.py

from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """

    def has_permission(self, request, view):
        # We allow general access to the view endpoints because 
        # get_queryset() in the ViewSets already filters data 
        # to only show what the user is allowed to see.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant of the conversation.
        This handles both Conversation objects and Message objects.
        """
        # If the object is a Conversation, check participants directly
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        
        # If the object is a Message, check the participants of the linked conversation
        elif isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()
        
        # Default strict fallback
        return False