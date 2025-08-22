"""Authentication endpoints."""

from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import structlog

from services.common.logging import get_logger
from services.api.database import get_db
from services.api.auth import (
    authenticate_user,
    create_user,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_user_by_email,
    verify_token
)
from services.api.models.user import User
from services.api.config import settings

logger = get_logger(__name__)
router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request model."""
    email: EmailStr
    password: str
    name: str


class RefreshRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    role: str
    subscription: str
    is_active: bool
    is_verified: bool


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """User login endpoint."""
    logger.info("Login attempt", email=request.email)
    
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """User registration endpoint."""
    logger.info("Registration attempt", email=request.email, name=request.name)
    
    # Check if user already exists
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = create_user(db, request.email, request.name, request.password)
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Refresh access token endpoint."""
    logger.info("Token refresh attempt")
    
    payload = verify_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout() -> Dict[str, Any]:
    """User logout endpoint."""
    # TODO: Implement token blacklisting
    logger.info("Logout attempt")
    
    return {"message": "Successfully logged out"}


@router.get("/status")
async def auth_status(current_user: User = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Check authentication status."""
    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role.value,
            "subscription": current_user.subscription.value
        }
    }


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    """Get user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        subscription=current_user.subscription.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified
    )
