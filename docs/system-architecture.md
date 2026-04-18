# Smart Urban Farming – System Architecture

## Overview

The Smart Urban Farming system is designed using a modular, scalable, and layered backend architecture.  
It enables plant data management, irrigation automation, and future integration with AI and IoT systems.

The system follows a modern API-driven design using FastAPI, with clear separation between request handling, business logic, and data storage.

This architecture allows the project to start as a functional MVP and evolve into a smart agriculture research platform.

---

## Version 1 Architecture (MVP)

![Version 1 Architecture](SystemArchitecture.png)

---


## System Components

The system consists of the following core components:

1. Frontend (Optional / Future)
2. Backend API (FastAPI)
3. PostgreSQL Database
4. External Plant APIs
5. Background Workers (Scheduler)
6. Future AI & IoT Modules

---

## Backend Architecture (Layered Design)

The backend follows a structured layered architecture:

Client (Swagger / Frontend)
↓
Routes (API Endpoints)
↓
Dependencies (Authentication - JWT)
↓
Schemas (Validation & Serialization)
↓
Services (Business Logic)
↓
Models (ORM)
↓
Database (PostgreSQL)


### Key Principles

- **Routes** handle HTTP requests  
- **Dependencies** manage authentication and shared logic  
- **Schemas** validate and structure data  
- **Services** contain business logic  
- **Models** represent database structure  

---

## Component Explanation

### 1. Frontend

The frontend is optional in Version 1 and can be replaced by Swagger or Postman.

Future implementations may use:
- React / Next.js
- Flutter
- Simple web dashboards

Responsibilities:
- User interaction
- Viewing plant data and notifications
- Managing plant collections

---

### 2. Backend API (FastAPI)

The FastAPI backend is the core system.

Responsibilities:
- Handle HTTP requests
- Validate input data
- Execute business logic
- Manage authentication (JWT)
- Trigger irrigation and notifications
- Communicate with database and external APIs


---

### 3. PostgreSQL Database

The database stores all persistent system data.

Core entities:
- users
- plants
- locations
- plant_groups
- notifications
- soil_conditions

Responsibilities:
- Store structured data
- Maintain relationships between entities
- Support query operations for services

---

### 4. External Plant APIs

The system integrates with external plant data providers.

Used APIs:
- Perenual API (current)
- Trefle API (future)

Responsibilities:
- Provide plant care data
- Supply species information
- Support recommendation features

---

### 5. Background Workers (Scheduler)

A background scheduler runs automated system tasks.

Responsibilities:
- Periodically check plant conditions
- Trigger irrigation logic
- Generate notifications

Flow:
Scheduler → Irrigation Service → Database → Notifications

This operates independently of user requests.

---

### 6. Future AI & IoT Modules

Planned extensions for advanced functionality.

AI:
- Companion plant recommendations
- Growth prediction
- Smart irrigation decisions

IoT:
- Soil moisture sensors
- Temperature and humidity monitoring
- Automated watering systems

---

## Data Flow (Request Lifecycle)

### Standard API Flow

Client Request
↓
Routes (HTTP Endpoint)
↓
Authentication (JWT Dependency)
↓
Schema Validation
↓
Service Layer (Business Logic)
↓
Database Query (Models)
↓
Service Processing
↓
Response Schema
↓
Return to Client


---

## Background Job Flow (Irrigation System)

Scheduler Trigger
↓
Irrigation Service
↓
Check plant conditions
↓
Update plant state
↓
Create or resolve notifications
↓
Database update


---

## External Data Flow

Client Request
↓
FastAPI Backend
↓
Check PostgreSQL
↓
If data missing:
→ Call External API (Perenual)
↓
→ Store in database
↓
Return result to client


---

## Version Roadmap

### Version 1 (Current MVP)

- FastAPI backend
- PostgreSQL database
- Perenual API integration
- Irrigation + notification system

Goal:
A functional smart farming backend system.

---

### Version 2

- AI-based plant recommendations
- Companion planting logic
- Cloud deployment
- Enhanced data models

Goal:
An intelligent decision-support system.

---

### Version 3

- IoT sensor integration
- Real-time environmental monitoring
- Automated irrigation
- Predictive analytics

Goal:
A fully automated smart farming platform.

---

## Design Principles

### Modular
Each layer is independent and replaceable.

### Scalable
New features (AI, IoT) can be added without restructuring.

### Separation of Concerns
Each layer has a clear responsibility.

### Data-Driven
Decisions are based on real plant and environmental data.

---

## Summary

The Smart Urban Farming system is built on:

- A layered FastAPI backend
- PostgreSQL for persistent storage
- External plant data integration
- Background automation via scheduler
- Future-ready AI and IoT extensions

This architecture supports gradual evolution from a simple API into a full smart agriculture platform.


