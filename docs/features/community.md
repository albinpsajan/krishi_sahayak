# Community Board

## Purpose
A moderated, crop-wise discussion board where farmers share field experience and officers post notices. It exists so advice is attributable — every post carries an author, a role-derived label and a publication state.

> **Moderation is not agronomic verification.** Publishing a post means an officer cleared it for the board, not that its advice is correct. Crop-disease claims still go through the Crop Cases + officer review workflow.

## Inputs
| Field | Constraint |
|---|---|
| `board` | `Paddy`, `Banana`, `Coconut`, `Pepper`, `Machinery`, `Market`, `Schemes` |
| `title` | 5–120 characters |
| `body` | 20–3000 characters |
| `status` (moderation) | `Published` or `Not published` |

The label is derived, never supplied by the client: `Expert notice` for `OFFICER`/`ADMIN`, otherwise `Farmer experience`.

## Outputs
Board listings ordered newest first. Farmers see published posts plus their own unpublished ones; officers and admins see everything. Each item exposes id, title, body, board, status, label, author display name and creation time.

## Main files
| File | Responsibility |
|---|---|
| `apps/community/models.py` | `CommunityPost` |
| `api/community_routes.py` | List, create, moderate — the whole HTTP boundary |
| `frontend/src/pages/CommunityPage.jsx` | Board browsing and posting |
| `frontend/src/pages/SupportPage.jsx` | Entry point / help content |

`PostInput` and `ModerationInput` are declared inline in the router because the feature has only two inputs and no service layer.

## Database models
`CommunityPost` (author_id → users, board, title, body, status default `Pending review`, label default `Farmer experience`, reviewed_by → users nullable, created_at).

## API endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/community` | ✓ | Board listing, role-filtered |
| POST | `/api/community` | ✓ | Create a post (starts as `Pending review`) |
| PATCH | `/api/community/{post_id}` | Officer | Publish or unpublish; records `reviewed_by` |

## AI components
None. Intent detection in `services/assistant_intent_service.py` can recognise scheme/question phrasing, but it never writes or approves a post.

## Dependencies
`farmer_profile` (author and moderator identities), `core` (db, security). Independent of every other feature — nothing reads `CommunityPost`.

## Known limitations
- **No replies or threads.** A post is a single message; there is no comment tree.
- **No reactions, likes, bookmarks, search, filtering or pagination.**
- **No edit or delete for authors** — once submitted, a post can only be unpublished by an officer.
- **No reporting or flagging flow**, and no rate limiting on post creation.
- **No push/email notification** when a post is published.
- Board list is a closed literal — adding a crop requires a code change.
- Posts are unmoderated AI-free text, so the board is a trust surface that currently relies on officer review alone.

## How to test
No dedicated suite. `tests/test_workflows.py` covers the create → moderate → visibility flow. A focused `tests/community/` package should assert that a farmer never receives another farmer's unpublished post, that officers see everything, and that the label is role-derived rather than client-controlled.
