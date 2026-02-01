# Auth Service

**Base path:** `/auth`
**Port:** 8001 (internal)

## Endpoints

| Method | Endpoints | Request Body/Query Params | Response |
| -------- | -------- | -------- | -------- |
| POST | `/register` | **Body:** `username, password, email, phonenumber` | `user_id, message` | 
| POST | `/login` | **Body:** `username, password` | `access_token, refresh_token, token_type` |
| POST | `/refresh` | **Body:** `refresh_token` |  `access_token, refresh_token, token_type` |  
| POST | `/logout` | **Head:** `Authorization` **Body:** `refresh_token` | `message` | 
| GET | `/users/me` | **Head:** `Authorization` | `username, password, email, phonenumber` | 
| POST | `/users/me` | **Head:** `Authorization` **Body:** `username, email, phonenumber` | `username, email, phonenumber` |
| PUT | `/users/me/password` | **Head:** `Authorization` **Body:**  `old_password, new_password` | `message` |
| GET | `/users/{user_id}` | **Head:** `Authorization` **Path:** `user_id` | `username, user_id` |

  
