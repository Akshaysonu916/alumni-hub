# myapp/context_processors.py

# from .models import Notification

# def notification_count(request):
#     if request.user.is_authenticated:
#         count = Notification.objects.filter(user=request.user).count()
#     else:
#         count = 0
#     return {'notification_count': count}


from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        return {
            'unread_notification_count': Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        }
    return {}