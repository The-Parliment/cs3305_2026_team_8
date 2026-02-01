# Group Service

**Base path:** `/groups`
**Port:** 8003 (internal)

## Endpoints

| Method | Endpoints | Request Body/Query Params | Response |
| -------- | -------- | -------- | -------- |
| POST | `/create` | **Head:** `Authorization` **Body:** `group_name` `description` `visibility (Public/Private)` | `group_id` `group_name` | 
| GET | `/list` | **Head:** `Authorization` | array of: `group_id`, `group_name`, `group_description` |
| POST | `/join` | **Head:** `Authorization` **Body:** `group_id` | `message` | 
| POST | `/leave` | **Head:** `Authorization` **Body:** `group_id` | `message` |
| GET | `/mygroups` | **Head:** `Authorization` | array of: `group_id`, `group_name`, `group_description` |
| GET | `/listmembers` | **Head:** `Authorization` **Body:** `group_id` | array of `user_id`, `username`, |
| DELETE | `/removemember` | **Head:** `Authorization` **Body:** `user_id` | `message` |

 

