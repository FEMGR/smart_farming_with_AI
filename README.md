# Smart Urban Farming System

A FastAPI-based smart farming backend for managing plants, locations, irrigation, notifications, species data, and companion planting recommendations.

The system has moved beyond the original MVP. It now includes JWT authentication, user-scoped plant and location management, Perenual species enrichment with local caching, Prolog-backed companion planting logic, scheduled watering checks, and an automated test suite.

## Repository

GitHub: https://github.com/xueshuijing/Smart_Urban_Farming_System

## Current Capabilities

- User registration and OAuth2-compatible JWT login
- User-scoped CRUD for plants and growing locations
- Species search and enrichment through the Perenual API
- Persistent species cache and local JSON species snapshots
- Smart irrigation checks based on plant watering intervals
- Manual and bulk watering actions
- Notification creation and read tracking for watering reminders
- Companion planting recommendations powered by Prolog rules
- Companion grouping and basic layout generation for planting plans
- Centralized configuration, logging, error handling, and database access
- Alembic database migrations
- Pytest coverage for auth, plants, locations, irrigation, notifications, species, and Prolog recommendations

## Architecture

![System Architecture](docs/SystemArchitecture.png)

The backend is organized as a layered FastAPI application:

- Routes receive HTTP requests and validate payloads.
- Schemas define request and response contracts.
- Services contain business logic for auth, plants, locations, species, irrigation, notifications, and recommendations.
- Models define SQLAlchemy database tables.
- The database layer provides sessions and engine configuration.
- Prolog rules provide companion planting reasoning through SWI-Prolog.
- Background workers run scheduled watering checks.

Additional documentation:

- [System architecture](docs/system-architecture.md)
- [Technology selection](docs/technology-selection.md)
- [Data flow diagram](docs/DataFlowDiagram.png)

## Technology Stack

| Area | Tools |
| --- | --- |
| Backend API | FastAPI, Uvicorn, Starlette |
| Language | Python 3.10 |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Authentication | JWT, OAuth2 password flow, Passlib, bcrypt |
| External data | Perenual API |
| Reasoning engine | SWI-Prolog |
| Scheduling | APScheduler |
| Testing and quality | Pytest, pytest-cov, Black, Flake8, pre-commit |
| Frontend | Streamlit placeholder in `frontend/streamlit_app.py` |

## Project Structure

```text
smart-farming-system/
├── backend/
│   ├── main.py                       # FastAPI application entry point
│   ├── alembic/                      # Database migrations
│   ├── app/
│   │   ├── api/                      # API dependencies and v1 routes
│   │   ├── core/                     # Config, constants, security, logging, errors
│   │   ├── database/                 # SQLAlchemy engine/session setup
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── services/                 # Business logic
│   │   │   └── prolog/               # Prolog service bridge
│   │   ├── utils/                    # Normalization, matching, reliability helpers
│   │   └── workers/                  # Background scheduler
│   ├── cache/species_snapshots/      # Local species detail snapshots
│   └── docker-compose.yml            # Backend/PostgreSQL compose file
├── logic_companion_planting/         # Prolog facts, rules, and loader
├── docs/                            # Architecture and technology documentation
├── scripts/                         # Data backfill and conversion utilities
├── tests/                           # Automated tests and fixtures
├── frontend/                        # Streamlit app placeholder
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Prerequisites

- Python 3.10
- PostgreSQL
- SWI-Prolog, available as `swipl`
- A Perenual API key for live species search and detail lookups

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/smart_farming
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
PERENUAL_API_KEY=your-perenual-api-key
DEBUG=True
APP_NAME=Smart Urban Farming System
API_VERSION=v1
```

`DATABASE_URL` and `SECRET_KEY` are required at startup.

## Local Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create the PostgreSQL database:

```bash
createdb smart_farming
```

4. Run migrations:

```bash
cd backend
PYTHONPATH=. alembic upgrade head
cd ..
```

5. Start the API from the repository root:

```bash
PYTHONPATH=backend uvicorn backend.main:app --reload
```

6. Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## API Overview

The current API is mounted directly at the root path. Authentication is required for plant, location, irrigation, notification, and recommendation endpoints.

| Area | Endpoint |
| --- | --- |
| Health | `GET /` |
| Auth | `POST /auth/register` |
| Auth | `POST /auth/login` |
| Species | `GET /species/suggest?query=tomato` |
| Plants | `GET /plants/` |
| Plants | `POST /plants/` |
| Plants | `POST /plants/with-species?species_id=...` |
| Plants | `GET /plants/{plant_id}` |
| Plants | `PATCH /plants/{plant_id}` |
| Plants | `DELETE /plants/{plant_id}` |
| Recommendations | `GET /plants/recommendations` |
| Locations | `GET /locations/` |
| Locations | `POST /locations/` |
| Locations | `GET /locations/{location_id}` |
| Locations | `PATCH /locations/{location_id}` |
| Locations | `DELETE /locations/{location_id}` |
| Irrigation | `GET /irrigation/needs-water` |
| Irrigation | `POST /irrigation/water/{plant_id}` |
| Irrigation | `POST /irrigation/water-all` |
| Notifications | `GET /notifications/` |
| Notifications | `PUT /notifications/{notification_id}/read` |

## Companion Planting Logic

Companion planting recommendations are generated by the Prolog knowledge base in `logic_companion_planting/`.

The Python service at `backend/app/services/prolog/prolog_service.py` calls SWI-Prolog with `swipl`, parses the output, and returns structured recommendation data to the plant service. The recommendation response includes:

- Existing plant interactions
- Recommended and avoided pairs
- Grouped planting suggestions
- Generated layout data
- New companion suggestions for the user's current plants

## Species Data and Caching

Species search and enrichment are handled by `backend/app/services/perenual_service.py`.

The service uses:

- Perenual API search and detail endpoints
- In-memory response caching
- Database-backed species cache records
- Local JSON snapshots in `backend/cache/species_snapshots/`
- Fuzzy species matching through `rapidfuzz`

Plants can still be created manually when no confident species match is found.

## Running Tests

Run the full test suite from the repository root:

```bash
PYTHONPATH=backend pytest
```

Run with coverage:

```bash
PYTHONPATH=backend pytest --cov=backend --cov=tests
```

The tests use an in-memory SQLite database and override the FastAPI database dependency.

## Development Notes

- The FastAPI app entry point is `backend.main:app`.
- Most protected routes depend on the JWT current-user dependency.
- The scheduler starts with the FastAPI lifespan hook and shuts down when the app stops.
- Alembic migrations live under `backend/alembic/versions/`.
- `frontend/streamlit_app.py` currently exists as a placeholder and does not yet implement a dashboard UI.
