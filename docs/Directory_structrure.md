# Directory Structure

```text
.
├── api_gateway/                        # Nginx reverse proxy — public entry point
│   ├── certs/                          # TLS certificates (cert.pem, key.pem)
│   └── conf.d/default.conf             # Routing rules: strips service prefix, proxies to backend
│
├── backend/                            # All FastAPI microservices
│   ├── auth/                           # Authentication & user profiles
│   │   ├── main.py
│   │   ├── security.py                 # JWT minting (access + refresh tokens)
│   │   └── structures.py              # Local Pydantic request/response models
│   ├── circles/                        # Circle invite/membership management
│   │   ├── main.py
│   │   └── circles_model.py
│   ├── events/                         # Event creation, RSVP, search
│   │   ├── main.py
│   │   ├── events_database.py          # Helper queries (event_exists, is_host, is_invited…)
│   │   └── events_model.py
│   ├── groups/                         # Public/private group management
│   │   ├── main.py
│   │   ├── models.py
│   │   └── crud.py
│   ├── proximity/                      # Real-time location via Valkey geospatial
│   │   ├── main.py
│   │   └── tokens.py                   # Placeholder — passes username through; TODO: decode JWT
│   └── user/                           # Follow/friend relationships
│       ├── main.py
│       └── user_model.py
│
├── common/                             # Shared library — mounted into every backend container
│   ├── JWTSecurity.py                  # decode_and_verify() — used by all services
│   ├── JWTSettings.py                  # JWT config (secret, algorithm, TTLs) via env vars
│   ├── FastAPIAuth.py                  # Reusable FastAPI auth dependency
│   ├── clients/
│   │   └── client.py                   # Async HTTP client for inter-service calls
│   └── db/
│       ├── base.py                     # SQLAlchemy declarative base
│       ├── db.py                       # get_db() session context manager
│       ├── engine.py                   # Engine initialisation
│       ├── session.py                  # Session factory
│       └── structures/
│           └── structures.py           # *** Single source of truth for all ORM models ***
│
├── frontend/                           # Server-side rendered UI (FastAPI + Jinja2)
│   ├── main.py                         # Route handlers — calls backend APIs, renders templates
│   ├── forms.py                        # WTForms definitions
│   ├── templates/                      # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── circle.html
│   │   ├── community.html
│   │   ├── events_map.html
│   │   ├── home.html
│   │   ├── invites.html
│   │   ├── myevents.html
│   │   ├── profile.html
│   │   └── forms/                      # login, register, edit_event, change_details
│   └── static/
│       └── js/
│           ├── map.js                  # Proximity map (nearby circle members)
│           ├── events_map.js           # Events map layer
│           └── create_event_map.js     # Location picker for event creation
│
├── docker-compose.yml                  # Wires all services, networks, env vars, ports
├── mkdocs.yml                          # Builds docs/ into a documentation site
└── README.md
```

## Architecturally Significant Notes

**`common/`** is not a service. It is a shared Python package mounted as a volume into every backend container at runtime. Any change to `common/` affects all services simultaneously — there is no independent versioning.

**`common/db/structures/structures.py`** is the single source of truth for the entire database schema. All services import ORM models from here. A schema migration must be coordinated across all services.

**`common/clients/client.py`** is used for all inter-service HTTP calls. It forwards the `access_token` cookie so downstream services can authenticate the request using their own `decode_and_verify()` call — no service needs to call auth to validate a token.

**`proximity/tokens.py`** is a placeholder. It currently returns the username from the request body directly. It is meant to be updated to decode a JWT when the frontend starts sending proper tokens to the proximity service.

**`frontend/main.py`** is a FastAPI application, not a static file server. It contains route handlers that call the backend APIs and pass data into Jinja2 templates.

**`api_gateway/conf.d/default.conf`** is where all public routing lives. It strips the service prefix before proxying (e.g. `/auth/login` → `/login`). Each backend service is unaware it sits behind a gateway.

**`proximity/`** is the only service with no dependency on PostgreSQL. It connects to Valkey for geospatial storage.