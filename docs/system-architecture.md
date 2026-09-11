# Smart Urban Farming - System Architecture

## Overview

The Smart Urban Farming system is a comprehensive, layered, and API-driven ecosystem for plant management, AI-powered computer vision & predictive modeling, companion planting logic, knowledge engineering, production planning, and automated irrigation workflows.

The backend acts as the composition root, exposing a FastAPI REST API, persisting application state in PostgreSQL, executing ML inference pipelines, enriching plant species data via local data banks and external caches, delegating companion and ecological reasoning to SWI-Prolog, and running background workflows through APScheduler.

## Current Architecture

![System Architecture](/home/graubo/PyCharmMiscProject/smart-farming-system/docs/2026_09_SystemArchitecture.jpeg)

## Components

1. Client applications
2. FastAPI backend
3. Service layer
4. PostgreSQL database
5. Prolog knowledge base
6. AI & Machine Learning Engine
7. External and local species data
8. Background scheduler

## Client Applications

The system currently has three primary client surfaces:

- Swagger/OpenAPI at `/backend/app/api` for direct API inspection and testing
- Streamlit dashboard in `frontend/streamlit_app.py`
- Expo React Native mobile client in `mobile/`

All clients communicate with the FastAPI backend over HTTP. Authenticated workflows use JWT bearer tokens issued by the backend.


## Backend API

The FastAPI backend is defined in `backend/main.py`.

Responsibilities:

- Create the FastAPI app
- Register API routers
- Configure logging and centralized exception handling
- Initialize SQLAlchemy models and database connectivity
- Load local plant taxonomy and growth facts on startup
- Start and stop the background scheduler through the lifespan hook

## Layered Backend Design

```text
Client request
    |
FastAPI route
    |
Authentication dependency
    |
Pydantic schema validation
    |
Service layer
    |
SQLAlchemy models / Prolog bridge / external data clients
    |
PostgreSQL / Prolog knowledge base / Perenual / local snapshots
```

## AI & Predictive Pipeline (`ai/`)

The system includes a dedicated ML/AI workspace handling multi-modal tasks (Vision, Tabular, Data Generation).

### Workflow:
1. **Ingestion & Generation (`ai/ingestion/`, `ai/data_generation/`)**: Ingests multi-source raw agricultural data and generates synthetic augmentation samples where needed.
2. **Preprocessing (`ai/preprocessing/parser/`)**: Cleans, parses, and normalizes input data, placing formatted output into `ai/datasets/processed/`.
3. **Experiments & Training (`ai/experiments/`, `ai/training/`)**: Reads from `datasets/processed/` to conduct training runs across core ML frameworks (`ai/core/ml/`, `ai/core/tabular/`, `ai/core/vision/`).
4. **Model Artifacts (`ai/saved_models/`, `ai/artifacts/`)**: Trained model checkpoints are stored upon evaluation.
5. **Task Execution (`ai/tasks/`, `ai/inference/`)**: Exposes domain-specific tasks utilized by the backend:
   - Crop Recommendation
   - Disease Detection & Prediction
   - Growth & Yield Prediction
   - Irrigation Requirement Prediction
   - Pest Detection
   - Plant Identification

```text
[ Raw Data / Ingestion ]
           │
           ▼
 [ Preprocessing / Parser ]
           │
           ▼
  [ Processed Datasets ] ───► [ Experiments & Training ]
                                         │
                                         ▼
                                 [ Saved Models ]
                                         │
                                         ▼
                             [ Task Inference Services ]

```

Key principles:

- Routes handle HTTP concerns.
- Dependencies enforce authentication and provide shared request context.
- Schemas define request and response contracts.
- Services contain business logic.
- Models define persistent database tables.
- Knowledge services isolate Prolog and plant-data reasoning from route handlers.

## Persistence

PostgreSQL stores user and application state. SQLAlchemy models are registered from `backend/app/models/__init__.py`, and Alembic migrations live in `backend/alembic/versions/`.

Core model areas:

- Users and authentication
- Plants, locations, plant groups, plant actions, plant growth, soil conditions
- Species cache and growth facts
- Notifications
- Farm sections, crop plans, crop plan groups, production batches, harvest records
- Lifecycle events, growth snapshots, timeline snapshots

## Knowledge and Data Enrichment

The Prolog knowledge base in `logic_companion_planting/` contains facts, taxonomy, and rules for companion planting, environment compatibility, plant relationships, disease, pests, insects, layout, weather, and sources.

Python services call SWI-Prolog through `backend/app/services/prolog/prolog_service.py` and normalize results for API responses. This supports companion recommendations, grouping, layout generation, pest host lookups, deterrent suggestions, predator relationships, and ecological support data.

Species enrichment is handled by `backend/app/services/perenual_service.py` using:

- Perenual API search and detail endpoints
- In-memory response caching
- Database-backed cache records
- Local JSON snapshots in `backend/cache/species_snapshots/`
- Fuzzy matching with `rapidfuzz`

## Background Job Flow

APScheduler runs outside the HTTP request lifecycle.

```text
Scheduler trigger
    |
Open database session
    |
Load users
    |
Irrigation service checks each user's plants
    |
Create or update watering notifications
    |
Close database session
```

The scheduler starts during FastAPI startup and currently runs irrigation checks every 10 minutes, plus a startup run.

## Standard Request Flow

```text
Client
    |
FastAPI route
    |
JWT dependency
    |
Schema validation
    |
Domain service
    |
Database, Prolog, cache, or Perenual call
    |
Response schema
    |
Client
```

## Planning Flow

```text
Client creates sections or crop plans
    |
Planning service validates capacity and ownership
    |
Production models store sections, crop plans, and generated batches
    |
Polyculture planner asks Prolog for companion suitability and layout data
    |
Confirmed plans are persisted for later viewing and management
```

## Design Principles

- Keep HTTP handling, business logic, persistence, and reasoning concerns separate.
- Use user-scoped queries for protected resources.
- Prefer local caches and snapshots when available to reduce external API dependency.
- Keep Prolog reasoning behind Python service boundaries.
- Use migrations for schema changes and tests for behavior-sensitive flows.
