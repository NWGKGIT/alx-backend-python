from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from messaging.models import Message 

# Task 5: Cache this view for 60 seconds
@cache_page(60)
def conversation_view(request, message_id):
    # Task 3: Advanced ORM
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver')
                       .prefetch_related('replies'),
        id=message_id
    )
    return render(request, 'conversation.html', {'message': message})