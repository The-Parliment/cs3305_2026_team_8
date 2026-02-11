# Circle Service

The concept of a circle, is a grouping of users(people), Which is tightly controlled, e.g. a friendgroup.
For simplicity we will assume a user can only be __ONE__ circle.
The pier _GROUP SERVICE_ will allow users to join multiple groupings of individuals.

**Base path:** `/circles`
**Port:** 8002 (internal)

## Endpoints

| Method | Endpoints | Request Body/Query Params | Response |
| -------- | -------- | -------- | -------- |
| POST | `/invite` | **Head:** `Authorization` **Body:** `inviter, invitee` | `message` | 
| GET | `/getinvites` | **Head:** `Authorization` | Array of: `inviter_usernames` |  
| POST | `/accept` | **Head:** `Authorization` **Body:** `inviter, invitee` |  `message` | 
| POST | `/decline` | **Head:** `Authorization` **Body:** `inviter, invitee` | `message` |
| GET | `/mycircle` | **Head:** `Authorization` | Array of: `invitee_usernames` |
| POST | `/remove` | **Head:** `Authorization` **Body:** `inviter, invitee` | `message` |

