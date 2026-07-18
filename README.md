# Smart Urban Farming System

A full-stack smart farming system for managing plants, growing locations, watering tasks, production planning, lifecycle records, species enrichment, and Prolog-backed companion planting decisions.

The current system includes a FastAPI backend, PostgreSQL persistence, a Streamlit dashboard, an Expo React Native mobile client, SWI-Prolog reasoning, local species and knowledge caches, scheduled irrigation checks, and an automated test suite.

## Repository

GitHub: https://github.com/xueshuijing/Smart_Urban_Farming_System

## Current Capabilities

- User registration and OAuth2-compatible JWT login
- User-scoped plant, location, irrigation, notification, planning, lifecycle, and production data
- Perenual species search and enrichment with database cache records and local JSON snapshots
- Local growth fact loading from the Prolog knowledge base into application storage
- Smart irrigation checks based on plant watering intervals
- Manual and bulk watering actions
- Watering notification creation and read tracking
- Companion planting recommendations powered by SWI-Prolog rules and facts
- Companion grouping, polyculture previews, persisted polyculture plans, and layout JSON generation
- Production planning for farm sections, crop plans, succession batches, harvest records, and yield summaries
- Lifecycle event and growth snapshot tracking
- Pest knowledge endpoints for pest details, deterrents, predators, and host plants
- Streamlit dashboard for authenticated plant care workflows
- Expo mobile client for backend-backed plant, planning, and care screens
- Centralized configuration, logging, error handling, database access, and Alembic migrations
- Pytest coverage across auth, plants, locations, irrigation, notifications, species matching, planning, layout, Prolog recommendations, and knowledge services

## Architecture

![System Architecture](docs/SystemArchitecture.png)

The system is organized around a layered API backend with separate clients and knowledge/data subsystems:

- **Clients:** Swagger/OpenAPI, the Streamlit dashboard, and the Expo mobile app call the FastAPI API.
- **API layer:** Routes handle HTTP requests, authentication dependencies enforce JWT user scope, and schemas validate request/response contracts.
- **Service layer:** Business services implement auth, plants, locations, species, irrigation, notifications, planning, lifecycle, production, pest knowledge, and companion recommendations.
- **Persistence:** SQLAlchemy models store application state in PostgreSQL, with Alembic managing schema migrations.
- **Knowledge and enrichment:** Perenual supplies species data, local JSON snapshots reduce API dependency, and SWI-Prolog evaluates companion planting, pest, ecology, environment, and layout rules.
- **Automation:** APScheduler runs watering checks outside the request/response cycle and creates notifications through the same service layer.

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
| Web dashboard | Streamlit |
| Mobile client | Expo, React Native, Expo Router, TypeScript |
| Testing and quality | Pytest, pytest-cov, Black, Flake8, pre-commit |

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
│   │   ├── services/                 # Business logic and Prolog bridge
│   │   ├── utils/                    # Normalization, matching, reliability helpers
│   │   └── workers/                  # Background scheduler
│   ├── cache/species_snapshots/      # Local species detail snapshots
│   └── docker-compose.yml            # Backend/PostgreSQL compose file
├── frontend/                         # Streamlit dashboard
├── mobile/                           # Expo React Native client
├── logic_companion_planting/         # Prolog facts, rules, taxonomy, and loader
├── plant_data_bank_scripts/          # Data bank extraction, enrichment, and Prolog export scripts
├── docs/                             # Architecture and technology documentation
├── scripts/                          # Data backfill and conversion utilities
├── tests/                            # Automated tests and fixtures
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Prerequisites

- Python 3.10
- PostgreSQL
- SWI-Prolog, available as `swipl`
- A Perenual API key for live species search and detail lookups
- Node.js and npm for the Expo mobile app

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/smart_farming
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
PERENUAL_API_KEY=your-perenual-api-key
TREFLE_API_KEY=
DEBUG=True
APP_NAME=Smart Urban Farming System
API_VERSION=v1
```

`DATABASE_URL` and `SECRET_KEY` are required at startup. `PERENUAL_API_KEY` is optional for cached/local workflows but required for live Perenual lookups.

## Local Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install backend dependencies:

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

The backend can also be started with Docker from the `backend` directory:

```bash
docker compose up --build
```

## API Overview

The API is mounted at the root path. Protected endpoints use the JWT current-user dependency.

| Area | Endpoint examples |
| --- | --- |
| Health | `GET /` |
| Auth | `POST /auth/register`, `POST /auth/login` |
| Species | `GET /species/suggest?query=tomato` |
| Plants | `GET /plants/`, `POST /plants/`, `POST /plants/with-species`, `POST /plants/{plant_id}/duplicate`, `PATCH /plants/{plant_id}`, `DELETE /plants/{plant_id}` |
| Recommendations | `GET /plants/recommendations` |
| Locations | `GET /locations/`, `POST /locations/`, `PATCH /locations/{location_id}`, `DELETE /locations/{location_id}` |
| Irrigation | `GET /irrigation/needs-water`, `POST /irrigation/water/{plant_id}`, `POST /irrigation/water-all` |
| Planning | `POST /planning/sections`, `GET /planning/sections`, `POST /planning/crop-plans`, `POST /planning/crop-plans/{crop_plan_id}/generate-batches` |
| Polyculture | `POST /planning/polyculture-preview`, `GET /planning/polyculture-plans`, `POST /planning/polyculture-confirm`, `DELETE /planning/polyculture-plans/{crop_plan_id}` |
| Lifecycle | `POST /lifecycle/events`, `GET /lifecycle/events`, `POST /lifecycle/growth`, `GET /lifecycle/growth` |
| Production | `POST /production/harvests`, `GET /production/harvests`, `GET /production/yield-summary` |
| Knowledge | `GET /knowledge/pests/{pest}`, `GET /knowledge/pests/{pest}/deterrents`, `GET /knowledge/pests/{pest}/predators`, `GET /knowledge/pests/{pest}/hosts` |
| Notifications | `GET /notifications/`, `PUT /notifications/{notification_id}/read` |

## Companion Planting and Knowledge Logic

Companion planting and pest knowledge are generated from the Prolog knowledge base in `logic_companion_planting/`.

The Python service at `backend/app/services/prolog/prolog_service.py` calls SWI-Prolog with `swipl`, parses the output, and returns structured recommendation data. The recommendation and planning flows use:

- Existing plant interactions
- Recommended and avoided pairs
- Companion grouping suggestions
- Polyculture layout data
- Pest host, deterrent, predator, and ecological support facts
- Local plant taxonomy, aliases, growth facts, environment facts, disease facts, weather facts, and source facts

## Species Data and Caching

Species search and enrichment are handled by `backend/app/services/perenual_service.py`.

The service uses:

- Perenual API search and detail endpoints
- In-memory response caching
- Database-backed species cache records
- Local JSON snapshots in `backend/cache/species_snapshots/`
- Fuzzy species matching through `rapidfuzz`

Plants can still be created manually when no confident species match is found.

## Streamlit Dashboard

Start the FastAPI backend first, then run the dashboard from the repository root:

```bash
streamlit run frontend/streamlit_app.py
```

The dashboard uses `http://127.0.0.1:8000` by default. To point it at a different backend:

```bash
SMART_FARMING_API_URL=http://localhost:8000 streamlit run frontend/streamlit_app.py
```

Authenticated dashboard tabs currently cover overview, plants, locations, irrigation, recommendations, planning, layout, notifications, species lookup, and pest query.

## Mobile App

Start the backend with a host reachable by the mobile target:

```bash
PYTHONPATH=backend uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then start Expo:

```bash
cd mobile
npm install
npx expo start
```

Configure the API URL from the app sign-in screen. Typical values are `http://localhost:8000` for web/iOS simulator, `http://10.0.2.2:8000` for Android emulator, and `http://YOUR_COMPUTER_LAN_IP:8000` for a physical phone.

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
- Most application routes depend on the JWT current-user dependency.
- The scheduler starts with the FastAPI lifespan hook and runs irrigation checks every 10 minutes.
- Startup loads plant taxonomy cache, synchronizes PostgreSQL ID sequences, and ensures local growth facts are loaded.
- Alembic migrations live under `backend/alembic/versions/`.
- The Streamlit frontend entry point is `frontend/streamlit_app.py`.
- The mobile app entry point is `mobile/package.json` through `expo-router/entry`.
