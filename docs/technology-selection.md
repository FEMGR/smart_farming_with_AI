# Smart Urban Farming – Technology Selection

## Overview

The Smart Urban Farming project is designed to be modular, scalable, and suitable for future research and real-world implementation.  
The technology stack and data sources were selected based on availability, scalability, ease of integration, and long-term sustainability.

The system is built to support a functional MVP (Version 1) while allowing expansion into AI-based plant monitoring and smart agriculture systems in later versions.

---

## Technology Stack

### Backend Framework: FastAPI

#### Why FastAPI was chosen

- Lightweight and fast performance
- Easy REST API development
- Good integration with machine learning libraries
- Simple database connectivity
- Suitable for modular and scalable systems
- Easy deployment to cloud environments

#### Role in the Project

- Plant API endpoints
- User plant tracking
- Plant recommendation system
- Communication between frontend and database
- Data processing layer

#### Future Expansion

- Microservices architecture
- AI model integration
- IoT system integration
- Cloud deployment (Docker or VPS)

---

## Database Selection

### PostgreSQL (Primary Database)

#### Why PostgreSQL was chosen

- Free and open source
- Highly reliable and stable
- Supports complex queries
- Strong data integrity
- Scalable for large datasets
- Widely used in research and production systems
- Supports structured and semi-structured data
- Compatible with AI and data analytics workflows
- Supports spatial and environmental data (GIS)

#### Role in Version 1

- Store plant data
- Store user plant collections
- Store watering requirements
- Store sunlight requirements
- Store plant growth tracking
- Store plant care schedules

#### Role in Version 2 and Version 3

- Environmental sensor data
- Smart irrigation data
- AI plant recommendation system
- Growth prediction data
- IoT integration
- Large-scale plant database

Using PostgreSQL from the beginning eliminates the need for database migration and ensures long-term system stability.

---

## Plant Data Sources

### Primary Source: Perenual API

#### Why Perenual was chosen

- Provides structured plant care data
- Watering requirements
- Sunlight requirements
- Soil information
- Growth and maintenance data
- Easy API integration
- Free tier available
- Suitable for MVP development

#### Role in Version 1

- Plant database
- Plant search system
- Care recommendations
- Plant information API

This enables fast development of a functional plant care system.

---

### Secondary Source: Trefle API (Global Expansion)

#### Why Trefle is considered

- Global plant database
- Scientific plant taxonomy
- Botanical classification
- Large plant dataset
- Research-level plant information
- Suitable for AI training

#### Role in Future Versions

- Scientific classification
- Global plant coverage
- Advanced plant recommendations
- AI dataset
- Research-level plant analysis

This allows expansion into global smart agriculture research.

---

## Future Data Sources

The system is designed to support additional datasets such as:

- PlantVillage dataset (plant disease detection)
- OpenFarm plant care database
- Kaggle plant datasets
- Government agriculture datasets
- Weather and environmental APIs

### Supported Features

- Plant disease detection
- Growth prediction
- Smart irrigation
- AI-based recommendations
- Environmental monitoring

---

## System Scalability Strategy

### Version 1 (MVP)

- FastAPI
- PostgreSQL
- Perenual API
- Basic plant care system
- Local development

**Goal:**  
Build a working smart urban farming application.

---

### Version 2 (Expansion)

- Trefle API
- AI plant recommendation
- Environmental data integration
- Cloud deployment
- Smart plant monitoring

**Goal:**  
Add intelligence and global plant data.

---

### Version 3 (Research and Smart Farming)

- AI models
- IoT sensor data
- Smart irrigation system
- Plant disease detection
- Predictive analytics

**Goal:**  
Create a smart urban farming research platform.

---

## Cost Consideration

All selected technologies are free or have free tiers.

| Technology | Cost |
|-----------|------|
| FastAPI | Free |
| PostgreSQL | Free |
| Perenual API | Free tier available |
| Trefle API | Free tier available |
| Kaggle datasets | Free |
| PlantVillage dataset | Free |
| OpenFarm | Free |

This ensures the project can be developed without financial barriers.

---

## Design Philosophy

### 1. Start with a Strong Foundation

Use PostgreSQL and FastAPI from the beginning to ensure scalability.

### 2. Build Modular Components

Allow easy integration of AI, IoT, and additional datasets.

### 3. Support Research and Real-World Use

Design the system for both academic research and practical smart farming applications.

---

## Summary

The Smart Urban Farming system uses:

- FastAPI for backend
- PostgreSQL as the main database
- Perenual for plant care data
- Trefle for global plant database
- Future AI and IoT integration


