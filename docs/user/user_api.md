# User Service

**Base path:** `/user`  
**Port:** 8006 (internal)

## Authentication

Most read endpoints use the authenticated caller from the `access_token` cookie. Mutation endpoints currently take explicit `inviter`/`invitee` in the request body.

## Endpoints

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| GET | `/` | — | `message` |
| POST | `/send_follow_request` | Body: `inviter, invitee` | `message, valid` |
| GET | `/get_follow_requests_received` | Cookie: `access_token` | `user_names[]` |
| GET | `/get_follow_requests_sent` | Cookie: `access_token` | `user_names[]` |
| GET | `/is_following/{username}` | Path: `username`, Cookie: `access_token` | `bool` |
| GET | `/follow_request_sent/{username}` | Path: `username`, Cookie: `access_token` | `bool` |
| POST | `/decline_follow_request` | Body: `inviter, invitee` | `message, valid` |
| POST | `/accept_follow_request` | Body: `inviter, invitee` | `message, valid` |
| GET | `/followers` | Cookie: `access_token` | `user_names[]` |
| GET | `/following` | Cookie: `access_token` | `user_names[]` |
| GET | `/friends` | Cookie: `access_token` | `user_names[]` |
| GET | `/search_users/{query}` | Path: `query`, Cookie: `access_token` | `user_names[]` |
| POST | `/withdraw_follow_request` | Body: `inviter, invitee` | `message, valid` |
| POST | `/unfollow` | Body: `inviter, invitee` | `message, valid` |
| GET | `/list_users` | — | `user_names[]` |

## Request Models

### `UsersRequest`

```json
{
  "inviter": "string",
  "invitee": "string"
}
```
