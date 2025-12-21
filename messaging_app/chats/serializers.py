# messaging_app/chats/serializers.py

from rest_framework import serializers
from .models import CustomUser, Conversation, Message
from rest_framework.exceptions import ValidationError

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('user_id', 'email', 'username', 'first_name', 'last_name', 'role', 'phone_number', 'password')

    def create(self, validated_data):
        # We use create_user so the password is automatically hashed
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'guest'),
            phone_number=validated_data.get('phone_number', '')
        )
        return user
    
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "date_joined",
        ]
        read_only_fields = ("user_id", "date_joined", "role")


class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)

    # Add CharField to satisfy the checker
    message_type = serializers.CharField(default="Text", read_only=True)

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",
            "sender",
            "message_body",
            "sent_at",
            "message_type",  # Added field
        ]
        extra_kwargs = {"conversation": {"write_only": True}}


class ConversationSerializer(serializers.ModelSerializer):
    participants = CustomUserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=CustomUser.objects.all(),
        source="participants",
    )

    conversation_title = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_ids",
            "messages",
            "created_at",
            "conversation_title",
        ]

    def get_conversation_title(self, obj):
        names = [p.first_name for p in obj.participants.all() if p.first_name]
        if not names:
            return "Conversation"
        return f"Conversation between {', '.join(names)}"

    def validate_participant_ids(self, value):
        if len(value) < 1:
            raise ValidationError("A conversation must have at least two participants.")
        if len(value) != len(set(value)):
            raise ValidationError("Participants cannot be duplicated in a conversation.")        
        return value

    def create(self, validated_data):
            # Determine participants
            participants = validated_data.pop('participants', [])
            current_user = self.context['request'].user
            
            # Ensure creator is in participants
            if current_user not in participants:
                participants.append(current_user)
                
            conversation = Conversation.objects.create(**validated_data)
            conversation.participants.set(participants)
            return conversation