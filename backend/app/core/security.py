"""
Core security module.

Key Point:
Provides authentication and security utilities for the application.

Responsibilities:
- Hash and verify user passwords
- Generate JWT access tokens
- Decode and validate JWT tokens
- Provide authenticated user via dependency injection

Architecture Role:
- System-level utility for authentication and security
- Used by services (token generation) and dependencies (token validation)

Layer Interaction:
- Communicates with: Database (user lookup), Models (user), Config
- Used by: Services (auth_service), Dependencies (get_current_user)

Data Flow:
User credentials processed (login)
        ↓
Password hashed or verified
        ↓
JWT token generated with payload
        ↓
Client sends token in Authorization header
        ↓
Token extracted via OAuth2PasswordBearer
        ↓
Token decoded and validated
        ↓
User retrieved from database
        ↓
User object returned to route

"""

#app.core.security.py

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.database.db import SessionLocal
from app.models.user import User

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hash plain password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """Generate JWT token"""

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decode JWT and return full User object
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        db.close()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None