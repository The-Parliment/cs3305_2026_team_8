# Groups Service

**Base path:** `/groups`  
**Port:** 8003 (internal)

## Authentication

All endpoints read identity from the `access_token` cookie. A few query-only endpoints (`/listmembers`, `/ismember`, `/group_exists`, `/group_info`, `/list`) do not require auth.

## Endpoints

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| POST | `/create` | `group_name, group_desc, is_private` | `group_id, group_name, group_desc, is_private` |
| POST | `/edit/{group_id}` | Path: `group_id` Body: `group_name, group_desc, is_private` | `message` |
| POST | `/delete/{group_id}` | Path: `group_id` | `message` |
| GET | `/list` | — | `group_list[]` |
| GET | `/mygroups` | — | `group_list[]` |
| GET | `/ownedgroups` | — | `group_list[]` |
| GET | `/group_info/{group_id}` | Path: `group_id` | Group info |
| GET | `/group_exists/{group_id}` | Path: `group_id` | `bool` |
| GET | `/ismember/{group_id}/{user}` | Path: `group_id, user` | `bool` |
| GET | `/listmembers/{group_id}` | Path: `group_id` | `members[]` |
| POST | `/invite/{user}/{group_id}` | Path: `user, group_id` | `message` |
| POST | `/invitecircle/{group_id}` | Path: `group_id` | `message` |
| POST | `/inviteallfriends/{group_id}` | Path: `group_id` | `message` |
| POST | `/accept_invite/{group_id}` | Path: `group_id` | `message` |
| POST | `/decline_invite/{group_id}` | Path: `group_id` | `message` |
| POST | `/request/{group_id}` | Path: `group_id` | `message` |
| POST | `/join_public_group/{group_id}` | Path: `group_id` | `message` |
| POST | `/accept_request/{group_id}/{user}` | Path: `group_id, user` | `message` |
| POST | `/decline_request/{group_id}/{user}` | Path: `group_id, user` | `message` |
| POST | `/leave/{group_id}` | Path: `group_id` | `message` |
| POST | `/remove/{group_id}/{user}` | Path: `group_id, user` | `message` |
| GET | `/get_group_invites` | — | `invites[]` |
| GET | `/get_group_requests` | — | `invites[]` |
| GET | `/get_this_group_invites/{group_id}` | Path: `group_id` | `invites[]` |
| GET | `/get_this_group_requests/{group_id}` | Path: `group_id` | `invites[]` |
| GET | `/user_is_invited/{group_id}` | Path: `group_id` | `bool` |
| GET | `/user_is_requested/{group_id}` | Path: `group_id` | `bool` |
| GET | `/friends_groups_exclusive` | — | `group_list[]` |

