# Proximity Service

**Base path:** `/proximity`  
**Port:** 8004 (internal)

## Authentication

`/get_friends` forwards the `access_token` cookie to the Circles service to get the authenticated user's circle. Other endpoints take identity from the request body directly — there is no auth guard enforced at the endpoint level yet.

## Endpoints

| Method | Endpoint | Request Body | Response |
|--------|----------|--------------|----------|
| GET | `/` | — | set-style message payload |
| POST | `/register_user` | `user_id, username` | plain string message |
| POST | `/update_location` | `username, latitude, longitude` | `message` |
| POST | `/get_friends` | `username, latitude, longitude, radius` | `friends[], count` |
| POST | `/get_everyone` | `username, latitude, longitude, radius` | `friends[], count` |

## Endpoint Notes

**`POST /update_location`** — stores the user's location in Valkey using `GEOADD` on the `user:locations` sorted set. Longitude is stored first (Valkey GEO convention).

**`POST /get_friends`** — calls the Circles service (`/mycircle`) forwarding the cookie, then does a `GEORADIUS` query on `user:locations`. Returns only users who are both within the radius **and** in the caller's circle. The caller is excluded from results.

**`POST /get_everyone`** — same `GEORADIUS` query but with no circle filtering. Returns all users within the radius except the caller. The comment in the source notes this is temporary until circle integration is complete — `/get_friends` now handles that properly.

## Response Shape — Friends

```json
{
  "friends": [
    {
      "username": "cillian",
      "latitude": 51.8985,
      "longitude": -8.4756,
      "distance": 0.42
    }
  ],
  "count": 1
}
```
`distance` is in km.