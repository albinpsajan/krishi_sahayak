# Farmer Digital Profile

## Purpose
Owns user accounts and profiles. The **single source of truth** for identity and farm data; every feature reads farmer facts through `profile_service` rather than keeping its own copies.

## Inputs
- Signup (email, username, password) → onboarding (full name, age, role, phone).

## Outputs
- JWT access tokens (24h) with `{sub, role, id}` claims.
- Profile payload with role-specific block (farm facts or officer facts).

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
- Passwords use SHA-256 for demo parity; production should use bcrypt/argon2.
- Username uniqueness is enforced via a separate unique index (SQLite ALTER TABLE limitation).

## How to test
```bash
python -m unittest tests.farmer_profile.test_auth_security tests.farmer_profile.test_profile_service -v
```
