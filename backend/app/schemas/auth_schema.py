"""
Schema definitions for authentication.

Key Point:
Defines validation and data structure for user registration and login.

Responsibilities:
- Validate incoming user data
- Structure registration and login response data

Architecture Role:
- Acts as a contract between client and authentication API endpoints

Layer Interaction:
- Used by: Routes, Services
"""
#app.schemas.auth_schema.py

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
