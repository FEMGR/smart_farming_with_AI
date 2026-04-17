"""
This file handles all authentication and security logic.

Purpose:
- Hash and verify passwords
- Generate JWT tokens
- Validate JWT tokens (authentication)

Architecture Role:
- Part of the "core" layer (system-level functionality)
- Used by services and routes

Key Features:
- Uses bcrypt for password hashing
- Uses JWT for stateless authentication
- Provides dependency to protect endpoints

Security Notes:
- SECRET_KEY must be kept safe (.env)
- Never store plain passwords
"""

from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import SECRET_KEY, ALGORITHM
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

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
    """
    Decode and validate a JWT token.

    Purpose:
    - Verify token integrity using SECRET_KEY
    - Extract payload data (e.g., user_id)

    Parameters:
        token (str): JWT token from client request

    Returns:
        dict | None:
            - Decoded payload if valid
            - None if token is invalid or expired

    Security Notes:
    - Uses HS256 algorithm (or configured ALGORITHM)
    - Prevents tampered tokens from being accepted

    Typical Payload Structure:
    {
        "sub": "user_id",
        "exp": expiration_timestamp
    }

    Why important:
    - Central point for JWT validation
    - Keeps authentication logic reusable across the app
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None