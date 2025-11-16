# messaging_app/chats/serializers.py

from rest_framework import serializers
from .models import CustomUser, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'role']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'message_body', 'sent_at']
        extra_kwargs = {
            # On create, the sender will be set from the request user (in the view)
            # but conversation must be provided.
            'conversation': {'write_only': True} 
        }

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    # Use PrimaryKeyRelatedField for writing (creating/updating) participants
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=CustomUser.objects.all(),
        source='participants' # Map this field to the 'participants' model field
    )

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'participant_ids', 'messages', 'created_at']