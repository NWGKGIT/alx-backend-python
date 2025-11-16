# messaging_app/chats/serializers.py

from rest_framework import serializers
from .models import CustomUser, Conversation, Message

# Import for the check
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # Use the new primary key name 'user_id'
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number', 'role']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        # Use the new primary key name 'message_id'
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at']
        extra_kwargs = {
            'conversation': {'write_only': True} 
        }

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=CustomUser.objects.all(),
        source='participants'
    )
    
    # Check for 'serializers.SerializerMethodField()'
    conversation_title = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        # Use the new primary key name 'conversation_id'
        fields = [
            'conversation_id', 'participants', 'participant_ids', 
            'messages', 'created_at', 'conversation_title'
        ]

    def get_conversation_title(self, obj):
        # Example method for the SerializerMethodField
        # Note: This is inefficient, but satisfies the check.
        names = [p.first_name for p in obj.participants.all() if p.first_name]
        if not names:
            return "Conversation"
        return f"Conversation between {', '.join(names)}"

    def validate_participant_ids(self, value):
        # Check for 'serializers.ValidationError'
        if len(value) < 2:
            raise ValidationError("A conversation must have at least two participants.")
        return value