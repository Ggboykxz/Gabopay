"""Authentication endpoints for dashboard access."""

import uuid
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from sqlalchemy import select
from passlib.hash import bcrypt

from apps.api.core.config import get_settings
from apps.api.core.database import get_db
from apps.api.models.merchant import Merchant, MerchantBalance

router = APIRouter()
security = HTTPBearer()


class RegisterRequest(BaseModel):
    """Registration request."""
    name: str
    email: EmailStr
    phone: str
    password: str


class LoginRequest(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    merchant: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


def create_access_token(merchant_id: uuid.UUID, email: str) -> str:
    """Create JWT access token."""
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(merchant_id),
        "email": email,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(merchant_id: uuid.UUID) -> str:
    """Create JWT refresh token."""
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(merchant_id),
        "exp": expires,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str, expected_type: Optional[str] = None) -> dict:
    """Verify and decode JWT token."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if expected_type and payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def get_current_merchant(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Merchant:
    """Get current authenticated merchant."""
    payload = verify_token(credentials.credentials, expected_type="access")
    async with get_db() as db:
        result = await db.execute(
            select(Merchant).where(Merchant.id == uuid.UUID(payload["sub"]))
        )
        merchant = result.scalar_one_or_none()
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Merchant not found",
            )
        return merchant


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new merchant account."""
    async with get_db() as db:
        result = await db.execute(
            select(Merchant).where(Merchant.email == request.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        merchant = Merchant(
            name=request.name,
            email=request.email,
            phone=request.phone,
            password_hash=bcrypt.hash(request.password),
        )
        db.add(merchant)
        await db.flush()

        balance = MerchantBalance(
            merchant_id=merchant.id,
            available_amount=0,
            pending_amount=0,
        )
        db.add(balance)

        return AuthResponse(
            access_token=create_access_token(merchant.id, merchant.email),
            refresh_token=create_refresh_token(merchant.id),
            merchant={
                "id": str(merchant.id),
                "name": merchant.name,
                "email": merchant.email,
            },
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login to merchant account."""
    async with get_db() as db:
        result = await db.execute(
            select(Merchant).where(Merchant.email == request.email)
        )
        merchant = result.scalar_one_or_none()

        if not merchant or not merchant.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not bcrypt.verify(request.password, merchant.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        return AuthResponse(
            access_token=create_access_token(merchant.id, merchant.email),
            refresh_token=create_refresh_token(merchant.id),
            merchant={
                "id": str(merchant.id),
                "name": merchant.name,
                "email": merchant.email,
            },
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token_endpoint(request: RefreshTokenRequest):
    """Refresh access token."""
    payload = verify_token(request.refresh_token, expected_type="refresh")

    async with get_db() as db:
        result = await db.execute(
            select(Merchant).where(Merchant.id == uuid.UUID(payload["sub"]))
        )
        merchant = result.scalar_one_or_none()

        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Merchant not found",
            )

        return AuthResponse(
            access_token=create_access_token(merchant.id, merchant.email),
            refresh_token=create_refresh_token(merchant.id),
            merchant={
                "id": str(merchant.id),
                "name": merchant.name,
                "email": merchant.email,
            },
        )


@router.get("/me")
async def get_me(merchant: Merchant = Depends(get_current_merchant)):
    """Get current merchant profile."""
    return {
        "id": str(merchant.id),
        "name": merchant.name,
        "email": merchant.email,
        "phone": merchant.phone,
        "country": merchant.country,
        "status": merchant.status,
        "kyc_status": merchant.kyc_status,
    }
