"""
Notifications feature (docs/features/notifications.md).

Purpose
-------
Creates and lists in-app notifications (English + Malayalam) for case
submissions, officer verifications and subsidy decisions. Other features call
notification_service.create_notification() instead of building rows directly.
"""

from apps.notifications import models, schemas, notification_service  # noqa: F401
