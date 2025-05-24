def notification_count(request):
    if request.user.is_authenticated:
        unread_count = request.user.notification_set.filter(status='unread').count()
    else:
        unread_count = 0
    return {'unread_notification_count': unread_count} 