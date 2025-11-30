from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager
# messaging/models.py

# Task 4: Custom Manager for Unread Messages
class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(read=False)

    # Renamed to match the expected pattern
    def unread_for_user(self, user): 
        # Optimized with .only() for necessary fields (Task 4)
        return self.get_queryset().filter(receiver=user).only('id', 'sender', 'content', 'timestamp') 
        # Added 'timestamp' and 'id' as these are often necessary fields
        
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Task 1: Field to track edits
    edited = models.BooleanField(default=False)
    
    # Task 3: Threaded conversations (replies)
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    # Task 4: Read status
    read = models.BooleanField(default=False)

    objects = models.Manager()
    unread = UnreadMessagesManager()

    def __str__(self):
        return f"Message {self.id} from {self.sender}"

class MessageHistory(models.Model):
    # Task 1: History Log
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    # Task 0: Notifications
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)