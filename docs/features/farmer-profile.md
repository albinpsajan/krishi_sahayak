# Farmer Digital Profile

## Purpose
Owns user accounts and profiles. The **single source of truth** for identity and farm data; every feature reads farmer facts through `profile_service` rather than keeping its own copies.

## Inputs
- Signup (email, username, password) → onboarding (full name, age, role, phone).

## Outputs
- JWT access tokens (24h) signed HS256, carrying the user email as `sub` plus `exp`.
- Profile payload with role-specific block (farm facts or officer facts).
- Farmer context for other features: `profile_service.get_farmer_context(db, user)` returns the single dict every other feature reads instead of duplicating farmer rows.

## Main files
| File | Responsibility |
|---|---|
| `apps/farmer_profile/models.py` | User, FarmerProfile, OfficerProfile |
| `apps/farmer_profile/profile_service.py` | get_farmer_context(), build_profile_response() |
| `apps/farmer_profile/schemas.py` | Auth/profile request & response schemas |
| `api/auth_routes.py` | register / login / details / me |
| `api/profile_routes.py` | GET /api/profile |
| `core/security.py` | Hashing, JWT, require_farmer / require_officer |

## Database models
User, FarmerProfile, OfficerProfile.

## API endpoints
`POST /api/auth/register` · `POST /api/auth/login` · `PUT /api/auth/details` · `GET /api/auth/me` · `GET /api/profile`

## AI components
None.

## Dependencies
None (other features depend on this one).

## Known limitations
- Passwords use PBKDF2-HMAC-SHA256 with 600 000 rounds and a per-user random salt. `verify_password()` still falls back to a bare SHA-256 comparison for hashes that predate the `pbkdf2_sha256$` prefix, so those legacy hashes remain weak until the user changes their password — there is no rehash-on-login.
- `JWT_SECRET_KEY` has a hard-coded development fallback in `config/settings.py`. Production **must** set it in the environment or every deployment shares one signing key.
- Tokens expire after 24 h with no refresh token, so the user must sign in again.
- `require_farmer()` and `require_officer()` both also admit `ADMIN`, but there is no admin-only surface and no admin UI.
- Username uniqueness is enforced via a separate unique index created by `run_lightweight_migrations()` (SQLite cannot add a UNIQUE constraint through `ALTER TABLE`).
- `get_current_user()` looks the user up by the `sub` (email) claim on every request, so a deleted or demoted user is correctly rejected — but role changes take effect only on the next request, never mid-token.

## How to test
```bash
python -m unittest tests.farmer_profile.test_auth_security tests.farmer_profile.test_profile_service -v
```
