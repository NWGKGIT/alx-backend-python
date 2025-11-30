from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete() # Triggers Task 2 Signal
        return redirect('home')
    return render(request, 'delete_account.html')

@login_required
def inbox(request):
    # Task 4: Use custom manager
    messages = Message.unread.for_user(request.user)
    return render(request, 'inbox.html', {'messages': messages})