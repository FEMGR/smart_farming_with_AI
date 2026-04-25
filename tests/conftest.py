# tests/conftest.py

import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from main import app
from app.database.db import Base, get_db
import pytest

'''
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_perenual_api():
    with patch("app.services.plant_service.suggest_species") as mock_suggest:
        # Define a side_effect function to handle different inputs
        def side_effect(db, query):
            if "Xylo-Zorg" in query:
                return []  # Return nothing for the gibberish test
            return [
                {
                    "id": 8042,
                    "common_name": "Nasturtium",
                    "scientific_name": "Tropaeolum",
                    "score": 100.0,
                    "source": "api"
                }
            ]

        mock_suggest.side_effect = side_effect
        yield mock_suggest

'''



pytest_plugins = [
    "tests.fixtures.plant_fixtures",
    "tests.fixtures.soil_fixtures",
]

# -----------------------------
# TEST DATABASE (IN-MEMORY)
# -----------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# -----------------------------
# DB FIXTURE (SHARED SESSION)
# -----------------------------
@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    Base.metadata.create_all(bind=connection)
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# -----------------------------
# CLIENT FIXTURE (USES SAME DB)
# -----------------------------
@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


# -----------------------------
# USER FACTORY
# -----------------------------
@pytest.fixture
def user_factory(client):
    def _create_user(email=None, password="test12345"):
        if not email:
            email = f"test_{uuid.uuid4()}@example.com"

        client.post("/auth/register", json={
            "email": email,
            "password": password
        })

        response = client.post("/auth/login", data={
            "username": email,
            "password": password
        })

        assert response.status_code == 200

        return response.json()["access_token"]

    return _create_user

# -----------------------------
# BACKWARD COMPATIBILITY FIXTURE
# -----------------------------
@pytest.fixture
def create_user(user_factory):
    return user_factory


# -----------------------------
# DEFAULT USER
# -----------------------------
@pytest.fixture
def token(user_factory):
    return user_factory()
