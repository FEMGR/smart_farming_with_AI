# Smart Urban Farming - System Architecture

## Overview

The Smart Urban Farming system is a layered, API-driven application for plant management, irrigation support, companion planting, production planning, lifecycle tracking, and pest knowledge lookup.

The backend is the composition root. It exposes a FastAPI API, persists application state in PostgreSQL, enriches species data from Perenual and local caches, delegates companion and ecological reasoning to SWI-Prolog, and runs scheduled irrigation checks through APScheduler.

## Current Architecture

![System Architecture](SystemArchitecture.png)

## Components

1. Client applications
2. FastAPI backend
3. Service layer
4. PostgreSQL database
5. Prolog knowledge base
6. External and local species data
7. Background scheduler

## Client Applications

The system currently has three primary client surfaces:

- Swagger/OpenAPI at `/docs` for direct API inspection and testing
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

Route groups currently cover:

- Auth
- Plants
- Species
- Locations
- Irrigation
- Notifications
- Planning and polyculture
- Lifecycle events and growth snapshots
- Production harvests and yield summaries
- Pest knowledge

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
