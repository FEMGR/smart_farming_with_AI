"""
Service layer for FastAPI (Authentication).

Key Point:
Handles business logic for user authentication and authorization.

Responsibilities:
- Validate user credentials (login)
- Handle user registration logic
- Generate JWT tokens
- Verify authentication data

Architecture Role:
- Central logic layer for authentication processes
- Delegates cryptographic operations to core security module

Layer Interaction:
- Communicates with: Models (user), Database, Core (security)
- Called by: Routes

Data Flow:
Validated credentials received from route
        ↓
User retrieved from database
        ↓
Password verified
        ↓
JWT token generated
        ↓
Result returned to route
"""

#app.services.auth_service.py

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
        password_hash=hashed
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
    if not verify_password(password, user.password_hash):
        return None
    return user


def login_user(db: Session, email: str, password: str):
    """Login user and return JWT token"""

    user = authenticate_user(db, email, password)

    if not user:
        raise ValueError("Invalid credentials")

    token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )

    return token
