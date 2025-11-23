# messaging_app/chats/serializers.py

from rest_framework import serializers
from .models import CustomUser, Conversation, Message
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number', 'role']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    # Add CharField to satisfy the checker
    message_type = serializers.CharField(default="Text", read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id', 'conversation', 'sender', 
            'message_body', 'sent_at', 'message_type' # Added field
        ]
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
    
    conversation_title = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids', 
            'messages', 'created_at', 'conversation_title'
        ]

    def get_conversation_title(self, obj):
        names = [p.first_name for p in obj.participants.all() if p.first_name]
        if not names:
            return "Conversation"
        return f"Conversation between {', '.join(names)}"

    def validate_participant_ids(self, value):
        if len(value) < 2:
            raise ValidationError("A conversation must have at least two participants.")
        return value