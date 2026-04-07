# 🌱 Smart Urban Farming System

A scalable smart urban farming platform designed to provide plant care recommendations, plant data management, and future AI-based plant monitoring and smart agriculture solutions.

This project builds a modular backend system using **FastAPI** and **PostgreSQL**, integrates real-world plant databases, and supports future **AI and IoT expansion** for smart agriculture research and development.

---

## 📌 Repository

GitHub: https://github.com/xueshuijing/Smart_Watering_System

---

## 🎯 Project Goals

- Build a smart plant care management system
- Provide plant watering and sunlight recommendations
- Store and manage plant data
- Integrate external plant databases
- Support AI-based plant recommendations
- Enable smart urban farming research and development
- Develop a scalable smart agriculture platform

---

## 🧠 System Overview

The system follows a **modular and scalable architecture**:

- FastAPI backend
- PostgreSQL database
- External plant APIs
- Streamlit dashboard
- Future AI and IoT integration

The project starts as a **working MVP** and gradually evolves into a **smart agriculture research platform**.

---

## 🏗️ Architecture

### Version 1 (MVP)

![Version 1 Architecture](docs/system-architecture-v1.drawio.png)

**Focus:**

- FastAPI backend
- PostgreSQL database
- Plant data management
- Perenual API integration
- Smart irrigation logic

---

### Future Architecture (Version 2 & Version 3)

![Future Architecture](docs/system-architecture-future.drawio.png)

**Future Expansion:**

- AI recommendation system
- Trefle plant database integration
- IoT sensor monitoring
- Cloud deployment
- Smart irrigation automation

---

## 🛠️ Technology Stack

### Backend
- FastAPI
- Python
- Uvicorn

### Database
- PostgreSQL
- SQLAlchemy

### External APIs
- Perenual API
- Trefle API (future)

### Frontend
- Streamlit

### Future Expansion
- Machine Learning
- IoT Sensors
- Cloud Infrastructure
- Smart Irrigation System

---

## 📂 Project Structure

```
smart-farming-system/

backend/
│
├── app/
│   ├── main.py
│   └── routes/
│       ├── plants.py
│       └── irrigation.py
│
├── database/
│   └── db.py
│
├── models/
│   └── plant.py
│
├── services/
│   ├── plant_service.py
│   └── irrigation_service.py
│
├── utils/
│   └── config.py
│
docs/
│   ├── system-architecture.md
│   ├── system-architecture-v1.drawio.png
│   ├── system-architecture-future.drawio.png
│   └── technology-selection.md
│
frontend/
│   └── streamlit_app.py
│
tests/

README.md
requirements.txt
venv/
```

---

## 📁 Folder Description

| Folder | Purpose |
|------|--------|
| backend/app | FastAPI entry point and API routes |
| backend/database | PostgreSQL connection and session |
| backend/models | SQLAlchemy data models |
| backend/services | Business logic (plants, irrigation) |
| backend/utils | Configuration and environment settings |
| docs | Architecture and technical documentation |
| frontend | Streamlit monitoring dashboard |
| tests | Unit and integration testing |

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/xueshuijing/Smart_Watering_System.git
cd Smart_Watering_System
```

---

### 2️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup PostgreSQL

Create database:

```bash
createdb smart_farming
```

or

```sql
CREATE DATABASE smart_farming;
```

---

### 5️⃣ Run FastAPI

```bash
uvicorn backend.app.main:app --reload
```

---

### 6️⃣ Open API Documentation

```
http://127.0.0.1:8000/docs
```

This opens the **Swagger API interface** for testing endpoints.

---

## 🔌 API Example

### Get All Plants

```
GET /plants
```

---

### Get Plant by ID

```
GET /plants/{id}
```

---

### Add Plant

```
POST /plants
```

---

## 📊 Streamlit Dashboard

Run frontend:

```bash
streamlit run frontend/streamlit_app.py
```

---

## 📚 Documentation

Detailed documentation is available in the **docs** folder.

- Technology Selection → `docs/technology-selection.md`
- System Architecture → `docs/system-architecture.md`

---

## 🚀 Version Roadmap

### Version 1 (MVP)

- FastAPI backend
- PostgreSQL database
- Perenual API
- Plant care system
- Smart irrigation logic

**Goal:**

Working smart urban farming API.

---

### Version 2

- Streamlit dashboard
- Trefle integration
- AI plant recommendation
- Cloud deployment

**Goal:**

Intelligent plant system.

---

### Version 3

- IoT sensors
- Smart irrigation automation
- Plant disease detection
- Predictive AI

**Goal:**

Smart urban farming research platform.

---

## 🎯 Design Principles

- Modular architecture
- Scalable system
- Data-driven decisions
- Research-oriented development
- Real-world usability
- Clean software engineering practices

---

## 🔮 Future Improvements

- Web dashboard
- Mobile application
- Plant image recognition
- Environmental monitoring
- Smart irrigation automation
- Cloud hosting
- AI plant health prediction
- Smart agriculture analytics

---

## 📜 License

This project is open-source and available for **educational and research purposes**.

---

## 👤 Author

**Smart Urban Farming Project**  
AI and Smart Agriculture Research Portfolio

GitHub: https://github.com/xueshuijing
