from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.timezone import make_aware
import datetime
from .models import Message

User = get_user_model()

@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '') 

    # Exclude the current user correctly
    users = User.objects.exclude(username=request.user.username)

    # Get the user object corresponding to the room_name (username)
    chat_user = get_object_or_404(User, username=room_name)

    # Filter chat messages between the current user and the selected user
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=chat_user)) |
        (Q(receiver=request.user) & Q(sender=chat_user))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))  

    chats = chats.order_by('timestamp') 

    user_last_messages = []

    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Fix timezone issue by using aware datetime
    min_aware_datetime = make_aware(datetime.datetime.min)

    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] and x['last_message'].timestamp else min_aware_datetime,
        reverse=True
    )

    return render(request, 'chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query 
    })
