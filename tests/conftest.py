# tests/conftest.py

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from app.database.db import Base, get_db
from app.workers.scheduler import scheduler

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
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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

    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
    except Exception:
        pass

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

        # Truncate password by bytes to prevent "password too long" errors from bcrypt
        password_bytes = password.encode("utf-8")
        truncated_password_bytes = password_bytes[:72]
        final_password = truncated_password_bytes.decode("utf-8", errors="ignore")  # Decode back to string for JSON

        print(f"DEBUG: Registering user with password (length {len(final_password)} chars, {len(final_password.encode('utf-8'))} bytes): '{final_password}'")

        reg_response = client.post("/auth/register", json={"email": email, "password": final_password})
        if reg_response.status_code not in [200, 201]:
            raise RuntimeError(f"Registration failed: {reg_response.status_code}: {reg_response.text}")

        response = client.post("/auth/login", data={"username": email, "password": final_password})

        if response.status_code != 200:
            raise RuntimeError(f"Login failed with {response.status_code}: {response.text}")

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
