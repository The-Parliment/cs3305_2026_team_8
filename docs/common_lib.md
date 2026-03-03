# Common Library

`common/` is a shared Python package mounted as a volume into every backend container. It is not a service — it has no port and runs no server. It provides four things: JWT security, database access, ORM models, and the inter-service HTTP client.

## Structure

```text
common/
├── JWTSecurity.py          # decode_and_verify() — validates tokens
├── JWTSettings.py          # JWT config loaded from environment variables
├── FastAPIAuth.py          # Reusable FastAPI dependency for protected routes
├── clients/
│   └── client.py           # Async HTTP client for inter-service calls
└── db/
    ├── base.py             # SQLAlchemy declarative base
    ├── db.py               # get_db() session context manager
    ├── engine.py           # Engine initialisation from env vars
    ├── session.py          # Session factory
    └── structures/
        └── structures.py   # All ORM models — single source of truth for DB schema
```

## `JWTSecurity.py`

Every service that needs to identify the caller uses `decode_and_verify()`:

```python
from common.JWTSecurity import decode_and_verify

claims = decode_and_verify(token, expected_type="access")
username = claims.get("sub")  # username is the subject claim
```

It validates: signature, expiry, issuer, audience, and the `typ` claim. Passing `expected_type="refresh"` on an access token raises a `ValueError` — refresh tokens cannot be used where access tokens are expected.

Services read the token from the cookie and extract the username like this in practice:

```python
def get_username_from_request(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    claims = decode_and_verify(token, expected_type="access")
    return claims.get("sub")
```

This pattern appears in every service. None of them need to call the auth service to validate a token.

## `JWTSettings.py`

Reads JWT configuration from environment variables. The `jwt_secret` and `jwt_algorithm` must be identical across all containers — they are set in `docker-compose.yml`.

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET` | Signing key |
| `JWT_ALGORITHM` | e.g. `HS256` |
| `JWT_ISSUER` | Validated on decode |
| `JWT_AUDIENCE` | Validated on decode |
| `ACCESS_TOKEN_MINUTES` | Access token lifetime |
| `REFRESH_TOKEN_DAYS` | Refresh token lifetime |

## `clients/client.py`

All inter-service calls go through this async HTTP client. The `access_token` cookie is forwarded manually so the downstream service can authenticate the caller using its own `decode_and_verify()`:

```python
from common.clients.client import get

response = await get(
    CIRCLES_INTERNAL_BASE,
    "mycircle",
    headers={"Cookie": f"access_token={request.cookies.get('access_token')}"}
)
```

## `db/db.py`

All services access the database through the same session context manager:

```python
from common.db.db import get_db

with get_db() as db:
    result = db.scalar(select(Events).filter_by(id=event_id))
```

## `db/structures/structures.py`

The single source of truth for the entire database schema. All services import ORM models from here — no service defines its own DB models.

| Model | Table | Primary owner |
|-------|-------|--------------|
| `User` | `users` | auth |
| `UserDetails` | `user_details` | auth |
| `UserRequest` | `requests` | shared across all services |
| `Group` | `groups` | groups |
| `Events` | `events` | events |

Any schema change must be made here. Since all services mount the same `common/` volume, a migration needs to be coordinated — there is no independent schema versioning per service.