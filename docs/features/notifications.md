# Notifications

## Purpose
In-app alerts for farmers and officers (English + Malayalam). One creation path so behavior stays consistent.

## Inputs
`create_notification(db, user_id, title, message, malayalam_message, notification_type, target_link)`

## Outputs
Notification rows listed at `GET /api/notifications`, newest first, with unread counts in the UI navbar.

## Main files
| File | Responsibility |
|---|---|
| `apps/notifications/notification_service.py` | Single creation helper |
| `apps/notifications/models.py` | Notification |
| `api/notification_routes.py` | List + mark-as-read |

## Database models
Notification (user_id, title, message, malayalam_message, is_read, type, target_link).

## API endpoints
`GET /api/notifications` · `PUT /api/notifications/{id}/read`

## AI components
None.

## Dependencies
Called by crop_cases, subsidies (and future features). Depends only on core otherwise.

## Known limitations
- In-app only; email/SMS dispatch is future work.
- No per-user preferences yet.

## How to test
Covered indirectly by workflow endpoints; direct unit tests are a follow-up (`tests/notifications/`).
