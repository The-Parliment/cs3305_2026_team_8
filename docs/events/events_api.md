# Events Service

**Base path:** `/events`  
**Port:** 8005 (internal)

## Authentication

All endpoints that act on behalf of the logged-in user read identity from the `access_token` cookie. Query-only endpoints that take all params from the path do not require auth.

## Endpoints

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| POST | `/create` | `title, description, latitude, longitude, datetime_start, datetime_end, public?` | `event_id` |
| GET | `/eventinfo/{event_id}` | Path: `event_id` | Event info |
| GET | `/search` | Body: `latitude, longitude, radius, title?, datetime_start?, datetime_end?, host?` | `events[]` |
| POST | `/invite/{username}` | Path: `username` Body: `event_id` | `message` |
| POST | `/invitecircle/{event_id}` | Path: `event_id` | `message` |
| POST | `/inviteallfriends/{event_id}` | Path: `event_id` | `message` |
| POST | `/invite_group/{event_id}/{group_id}` | Path: `event_id, group_id` | `message` |
| POST | `/attend/{event_id}` | Path: `event_id` | `message` |
| POST | `/decline/{event_id}` | Path: `event_id` | `message` |
| POST | `/accept/{event_id}/{username}` | Path: `event_id, username` | `message` |
| POST | `/request/{event_id}` | Path: `event_id` | `message` |
| POST | `/cancel/{event_id}` | Path: `event_id` | `message` |
| POST | `/edit/{event_id}` | Path: `event_id` Body: `title, description, datetime_start, datetime_end, latitude, longitude, public?` | `message` |
| GET | `/myevents` | — | `events[]` |
| GET | `/my_invites` | — | `events[]` |
| GET | `/my_event_requests` | — | `invites[]` |
| GET | `/all_events` | — | `events[]` |
| GET | `/events_hosted_by/{username}` | Path: `username` | `events[]` |
| GET | `/get_attendees/{event_id}` | Path: `event_id` | `lst[]` |
| GET | `/is_attending/{event_id}/{username}` | Path: `event_id, username` | `value: bool` |
| GET | `/is_invited/{event_id}/{username}` | Path: `event_id, username` | `value: bool` |
| GET | `/is_invited_pending/{event_id}/{username}` | Path: `event_id, username` | `value: bool` |
| GET | `/is_host/{event_id}/{username}` | Path: `event_id, username` | `value: bool` |
| GET | `/is_requested/{event_id}/{username}` | Path: `event_id, username` | `value: bool` |

