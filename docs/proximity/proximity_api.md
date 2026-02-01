# Proximity Service

**Base path:** `/proximity`
**Port:** 8004 (internal)

## Endpoints

| Method | Endpoints | Request Body/Query Params | Response |
| -------- | -------- | -------- | -------- |
| POST | `/updatelocation` | **Head:** `Authorization` **Body:** `longitude`, `latitude` | `message` `updated_at` |
| POST | `/setvisibility` | **Head:** `Authorization` **Body:** `visibility` (private/inner_circle/groups/public) | `visibility` `updated_at` |
| GET | `/friendslocation` | **Head:** `Authorization` **Body:** `radius` | array of `user_id` `username` `latitude` `longitude` `distance` |  
 

