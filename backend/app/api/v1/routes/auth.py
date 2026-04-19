"""
Route layer for FastAPI (Authentication).

Key Point:
Handles user authentication endpoints such as login and registration.

Responsibilities:
- Receive authentication requests (login/register)
- Validate input using schemas
- Call authentication service
- Return JWT tokens and user responses

Architecture Role:
- Entry point for authentication-related operations
- Delegates business logic to auth service layer

Layer Interaction:
- Communicates with: Services (auth_service), Schemas, Dependencies

Data Flow:
Client Request (login/register)
        ↓
Route receives request
        ↓
Schema validates input
        ↓
Auth service processes credentials
        ↓
JWT token generated
        ↓
Response returned to client
"""

#app.api.routes.auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.auth_schema import UserCreate, UserLogin, Token
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register endpoint"""
    try:
        new_user = register_user(db, user.email, user.password)
        return {
            "message": "User created",
            "email": new_user.email
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2-compatible login for Swagger UI
    """
    try:
        token = login_user(
            db,
            form_data.username, #email
            form_data.password
        )
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
