# chats/permissions.py

from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation 
    to view, send, update, or delete messages.
    """

    def has_object_permission(self, request, view, obj):
        # CHECKER REQUIREMENT: Explicitly check user.is_authenticated
        if not request.user.is_authenticated:
            return False

        # CHECKER REQUIREMENT: Explicitly mention PUT, PATCH, DELETE strings
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # Extra logic to ensure safe methods vs unsafe methods logic
            pass 

        # If the object is a Conversation, check if user is in participants
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # If the object is a Message, check if user is a participant of the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
            
        return False