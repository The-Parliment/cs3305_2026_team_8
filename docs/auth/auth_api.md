# Auth Service

**Base path:** `/auth`  
**Port:** 8001 (internal)

## Authentication

Protected endpoints require a valid JWT access token passed as a cookie named `access_token`.

## Endpoints

| Method | Endpoint | Request Body / Query Params | Response |
|--------|----------|-----------------------------|----------|
| POST | `/register` | **Body:** `username, password, email, phone_number, first_name?, last_name?` | `message, valid` |
| POST | `/login` | **Body:** `username, password` | `access_token, refresh_token, token_type` |
| POST | `/refresh` | **Body:** `refresh_token` | `access_token, refresh_token, token_type` |
| GET | `/users/me` | **Cookie:** `access_token` | `username, first_name, last_name, email, phone_number` |
| POST | `/users/me` | **Cookie:** `access_token` **Body:** `first_name?, last_name?, email, phone_number` | `message, valid` |
| GET | `/users/{username}` | **Cookie:** `access_token` **Path:** `username` | `username, first_name, last_name, email, phone_number` |
| GET | `/user_exists` | **Query:** `username` | `message, valid` |
| GET | `/email_exists` | **Query:** `username` | `message, valid` |
| GET | `/phone_number_exists` | **Query:** `username` | `message, valid` |



