"""
This file defines authentication API endpoints.

Purpose:
- Handle user registration requests
- Handle login requests
- Return JWT tokens

Architecture Role:
- Part of the "routes" layer
- Entry point for authentication operations

Key Principles:
- Routes should be thin
- Delegate logic to services
- Handle HTTP errors only
"""

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
        # ⚠️ Swagger uses "username", we treat it as email
        token = login_user(
            db,
            form_data.username,
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
