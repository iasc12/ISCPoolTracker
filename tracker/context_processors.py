from .models import Notification


def notifications(request):
    if not request.user.is_authenticated:
        return {
            "notifications": [],
            "unread_notifications": 0,
        }

    recent_notifications = Notification.objects.all()[:10]
    unread_count = Notification.objects.filter(
        is_read=False
    ).count()

    return {
        "notifications": recent_notifications,
        "unread_notifications": unread_count,
    }
