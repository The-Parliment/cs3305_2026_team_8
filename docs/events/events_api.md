# Events Service

**Base path:** `/events`
**Port:** 8005 (internal)

## Endpoints

| Method | Endpoints | Request Body/Query Params | Response |
| -------- | -------- | -------- | -------- |
| POST | `/create` | **Head:** `Authorization` **Body:** `title` `description` `date` `time` `location` | `event_id` `title` `description` `date` `time` `location` | 
| GET | `/eventinfo` | **Head:** `Authorization` **Body:** `event_id` | `event_id` `title` `description` `date` `time` `location` |
| GET | `/search` | **Head:** `Authorization` **Body:** `location?` `date_from` `date_to` | array of `event_id` `title` `date` `time` `location` |
| POST | `/rsvp` | **Head:** `Authorization` **Body:** `event_id` `status`(accept/maybe/decline) | `message` `status` |
| POST | `/invitecircle` | **Head:** `Authorization` **Body:** `event_id` | `message` |
| POST | `/invitegroup` | **Head:** `Authorization` **Body:** `event_id` | `message` |
| POST | `/cancel` | **Head:** `Authorization` **Body:** `event_id` | `message` `status: canceled` |
| PUT | `/edit` | **Head:** `Authorization` **Body:**  `event_id` `title` `description` `date` `time` `location` | `event_id` `title` `description` `date` `time` `location` |
| GET | `/myevents` |**Head:** `Authorization` | array of `event_id` `title` `description` `date` `time` `location` |

