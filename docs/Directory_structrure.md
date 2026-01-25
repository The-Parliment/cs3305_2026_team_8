
## Directory Birds Eye

```text
.                                  # Project root
├── api_gateway/                   # Nginx reverse proxy (API Gateway, serves public port 80)
│   ├── Dockerfile                 # Build config for API Gateway
│   └── conf.d/
│       └── default.conf           # Nginx backend routing config for gateway
├── backend/                       # All backend microservices
│   └── auth_service/              # Authentication service (FastAPI)
│       ├── Dockerfile             # Build config for auth service
│       ├── main.py                # FastAPI app for auth
│       ├── requirements.txt       # Python dependencies for auth
│       └── tests/                 # Unit and integration tests for auth_service
│           └── test_main.py       # Example test file for auth endpoints
├── docs/                          # Project documentation
│   ├── architecture.md            # System architecture diagrams and notes
│   └── end_to_end_flow.md         # End-to-end request/response flow
├── frontend/                      # Static frontend (HTML/JS/CSS)
│   ├── Dockerfile                 # Build config for frontend nginx
│   ├── index.html                 # Main HTML page
│   ├── js/                        # Frontend JavaScript
│   │   └── auth.js                # Auth-related JS logic
│   └── nginx.conf                 # Custom nginx config (serves on 8080)
├── docker-compose.yml             # Multi-service orchestration config
├── README.md                      # Quick start and general info
```
