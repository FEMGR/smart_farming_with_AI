"""
This file contains authentication business logic.

Purpose:
- Handle user registration
- Handle login validation
- Generate JWT tokens

Architecture Role:
- Part of the "services" layer (business logic)
- Called by routes, interacts with models

Key Principles:
- No HTTP logic here
- No FastAPI dependencies
- Pure logic only

Why important:
- Keeps routes clean
- Makes logic reusable and testable
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(db: Session, email: str, password: str):
    """Register a new user"""

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise ValueError("Email already registered")

    hashed = hash_password(password)

    user = User(
        email=email,
        hashed_password=hashed
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str):
    """Validate user credentials"""

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def login_user(db: Session, email: str, password: str):
    """Login user and return JWT token"""

    user = authenticate_user(db, email, password)

    if not user:
        raise ValueError("Invalid credentials")

    token = create_access_token(
        data={"sub": user.email}
    )

    return token
