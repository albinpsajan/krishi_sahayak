"""
Notification service - the single place notifications are created.

Other features call create_notification() with identifiers only; this module
owns persistence so notification behavior (types, defaults) is consistent.
"""

from apps.notifications.models import Notification


def create_notification(
    db,
    user_id: int,
    title: str,
    message: str,
    malayalam_message: str = None,
    notification_type: str = "info",
    target_link: str = None,
) -> Notification:
    """Creates (but does not commit) a notification row for a user."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        malayalam_message=malayalam_message,
        notification_type=notification_type,
        target_link=target_link,
    )
    db.add(notif)
    return notif
