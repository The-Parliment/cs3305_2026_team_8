# Circle Service

The concept of a circle, is a grouping of users(people), Which is tightly controlled, e.g. a friendgroup.
For simplicity we will assume a user can only be __ONE__ circle.
The pier _GROUP SERVICE_ will allow users to join multiple groupings of individuals.

**Base path:** `/circles`
**Port:** 8002 (internal)

## Endpoints

| Method | Endpoints | Request Body/Query Params | Response |
| -------- | -------- | -------- | -------- |
| POST | `/invite` | **Head:** `Authorization` **Body:** `username` | `invite_id ,status (Accepted, Rejected, Pending, No-User)` | 
| GET | `/getinvites` | **Head:** `Authorization` | Array of: `invite_id`, `inviters_username` |  
| POST | `/accept` | **Head:** `Authorization` **Body:** `invite_id` |  `circle_id` | 
| POST | `/decline` | **Head:** `Authorization` **Body:** `invite_id` | `message` |
| GET | `/mycircle` | **Head:** `Authorization` | Array of: `user_id`, `user_name` |
| POST | `/remove` | **Head:** `Authorization` **Body:** `username` | `message` |

