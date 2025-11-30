from django.db import models

# Task 4: Custom Manager for Unread Messages
class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(read=False)

    def unread_for_user(self, user): 
        # Optimized with .only() for necessary fields (Task 4)
        return self.get_queryset().filter(receiver=user).only('id', 'sender', 'content', 'timestamp')