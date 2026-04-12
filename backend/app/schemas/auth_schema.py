"""
This file defines Pydantic schemas for authentication.

Purpose:
- Validate incoming request data (register/login)
- Define response structure (JWT token)

Architecture Role:
- Part of the "schemas" layer
- Ensures clean and validated data between client and API

Key Notes:
- Prevents invalid input (e.g. wrong email format)
- Separates API data from database models
"""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
