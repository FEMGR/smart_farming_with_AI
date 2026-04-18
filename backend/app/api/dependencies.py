"""
Dependency layer for FastAPI.

Key Point:
Provides reusable dependencies for authentication and request handling.

Responsibilities:
- Extract authentication data from incoming requests
- Decode and validate JWT tokens
- Provide current user identity to route handlers

Architecture Role:
- Acts as a bridge between authentication (JWT) and route layer
- Keeps routes clean by separating authentication logic

Layer Interaction:
- Communicates with: Routes, Core (security)

Data Flow:
Client Request (Authorization Header: Bearer Token)
        ↓
OAuth2PasswordBearer extracts token
        ↓
Token is decoded and verified
        ↓
User identity extracted from payload
        ↓
Injected into route via Depends()

"""

#app.api.dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token

# This must match your login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)):
    """
    Extract current user ID from JWT token.

    Steps:
    1. Extract token from Authorization header
    2. Decode JWT payload
    3. Retrieve 'sub' field (user_id)
    4. Validate and convert to integer

    Returns:
        int: Authenticated user's ID

    Raises:
        HTTPException (401):
            - If token is invalid
            - If payload is malformed
            - If user_id is missing or invalid

    Security Notes:
    - Ensures only authenticated users can access protected routes
    - Prevents unauthorized access to user-specific data
    """
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
