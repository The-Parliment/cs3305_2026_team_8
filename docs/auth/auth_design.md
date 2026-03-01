# User Management Design

## Registration

When a user registers, the service receives a `POST /register` request, checks that the username, email, and phone number aren't already taken, and then saves the data into two tables that only the auth service owns:

- **`users`** — stores the username and bcrypt-hashed password.
- **`user_details`** — stores the profile info (name, email, phone number).

Both rows are written in the same database transaction so you never end up with half a user. If any of the uniqueness checks fail, the endpoint returns `valid: false` with a plain English message rather than crashing with an error, so the frontend can show the user something useful.

## Database Schema (ER Diagram)

```mermaid
erDiagram
    users {
        string username PK
        string hashed_password
    }

    user_details {
        string username PK
        string first_name
        string last_name
        string email
        string phone_number
    }

    requests {
        string field1 PK "Sender"
        string field2 PK "Receiver"
        string field3 PK "Context (optional)"
        enum   type   PK "FOLLOW_REQUEST | CIRCLE_INVITE | EVENT_INVITE | GROUP_INVITE"
        enum   status    "PENDING | ACCEPTED | REJECTED | CONFIRMED"
    }

    users ||--|| user_details : "has profile"
    users ||--o{ requests : "sends/receives (field1 or field2)"
```

> **Note on `Status` enum:** The full enum defines `PENDING`, `ACCEPTED`, `REJECTED`, and `CONFIRMED`. However, no service currently uses `REJECTED` or `CONFIRMED` — all services only write `PENDING` and `ACCEPTED`. These values exist in the schema for future use.

### The `requests` Table — Composite Primary Key

Most tables use a single auto-incremented `id` as the primary key. The `requests` table does something different — it uses **four columns together** as the primary key: `(field1, field2, field3, type)`. This is called a composite primary key.

The way it works is that the database only rejects a new row if **all four values** match an existing row at the same time. Any single column on its own isn't unique — the uniqueness only applies to the full combination.

What this gives us in practice:

- Darren (`field1`) sending a `FOLLOW_REQUEST` to Cillian (`field2`) → one row, stored fine.
- Darren sending a `CIRCLE_INVITE` to Cillian → also fine, `type` is different so the combination is unique.
- Darren trying to send a **second** `FOLLOW_REQUEST` to Cillian → rejected, because all four values are identical to the row already there.

`field3` defaults to `""` (empty string) and is only needed for request types that have extra context, like `EVENT_INVITE` (which event?) or `GROUP_INVITE` (which group?). For `FOLLOW_REQUEST` and `CIRCLE_INVITE` it just sits there as `""` — it still needs to be part of the key, it just doesn't carry any meaning for those types.

## Token Strategy — JWT

JWTs are used to authenticate users across all services. The `username` is embedded in the token's `sub` claim and the whole thing is signed with a shared secret. Any microservice that gets a valid token can pull out the username without needing to call the auth service.

In practice, services that need to act on behalf of a user (like the circles service) receive user identity directly via the request body — `inviter` and `invitee` are passed explicitly rather than being read from the token. The token is used to verify the request is authenticated, not to identify the users involved in the operation.

### Token Types

| Type | Lifetime | Purpose |
|------|----------|---------|
| Access | Short (e.g. 15 min) | Prove who you are on each API call |
| Refresh | Long (e.g. 7 days) | Get a new access token without logging in again |

Both tokens include `iss`, `aud`, `sub`, `iat`, `exp`, and a `typ` field (`"access"` or `"refresh"`). The `typ` field is checked on decode so a refresh token can't be sneaked in where an access token is expected.

### Login Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as frontend
    participant API as api_gateway
    participant Auth as auth_service
    participant DB as datastore
    participant Service as other_microservice

    Note over User, Service: Registration already done

    User->>FE: Fills in login form
    FE->>API: POST /auth/login {username, password}
    API->>Auth: POST /login {username, password}
    Auth->>DB: SELECT * FROM users WHERE username = ?
    DB-->>Auth: User row (username, hashed_password)

    Auth->>Auth: bcrypt.verify(password, hashed_password)
    Note right of Auth: username becomes the JWT sub claim

    Auth->>Auth: mint_access_token(sub="darren_dev")<br/>mint_refresh_token(sub="darren_dev")
    Auth-->>API: {access_token, refresh_token, token_type}
    API-->>FE: {access_token, refresh_token, token_type}
    FE->>FE: Store tokens in cookie

    Note over User, Service: Every call after this can identify the user from the token

    User->>FE: Does something that needs a service
    FE->>API: GET /some_service/endpoint (cookie: access_token)
    API->>Service: GET /endpoint (cookie: access_token)

    rect rgb(240, 248, 255)
        Note right of Service: Verify token is valid<br/>User identity passed in request body
        Service->>Service: decode_and_verify(token, expected_type="access")
    end

    Service-->>API: Response
    API-->>FE: Response
    FE-->>User: Shows result
```

## Token Refresh Flow

Access tokens are short-lived on purpose — if one gets stolen it expires quickly. When it runs out, the frontend uses the refresh token to get a new one without making the user log in again.

```mermaid
sequenceDiagram
    actor User
    participant FE as frontend
    participant API as api_gateway
    participant Auth as auth_service

    User->>FE: Does something (access token expired)
    FE->>API: POST /auth/refresh {refresh_token}
    API->>Auth: POST /refresh {refresh_token}
    Auth->>Auth: decode_and_verify(refresh_token, expected_type="refresh")
    Auth->>Auth: mint_access_token(sub=payload["sub"])
    Auth-->>API: {new access_token, original refresh_token, token_type}
    API-->>FE: {new access_token, original refresh_token, token_type}
    FE->>FE: Swap old access token for new one in cookie
    FE-->>User: Carry on as normal
```

The refresh token stays the same — only a new access token is issued.

## Password Storage

Passwords are hashed with **bcrypt** via `passlib` before being written to the database. The plain-text password is never stored or logged anywhere. When checking a login, `CryptContext.verify()` handles the comparison in a timing-safe way so you can't guess passwords by measuring response times.

## Uniqueness Checks

Before creating a new user, the service checks each of the following separately and returns a clear message if any of them are already taken:

- `username` — must be unique in `users`
- `email` — must be unique in `user_details`
- `phone_number` — must be unique in `user_details`

These checks are also available as standalone endpoints (`/user_exists`, `/email_exists`, `/phone_number_exists`) so the frontend can validate individual fields in real time as the user is filling in the registration form.