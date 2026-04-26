from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import AuthResponse


def _issue_session(db: Session, user: User) -> AuthResponse:
    access_token = create_access_token(user.id, user.is_manager)
    refresh_token = generate_refresh_token()
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days),
    )
    db.add(db_token)
    db.commit()
    db.refresh(user)
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, user=user)


def login(db: Session, email: str, password: str) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    if not user.is_manager:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager access required.")
    return _issue_session(db, user)


def refresh_session(db: Session, refresh_token: str | None) -> AuthResponse:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required.")

    token_hash = hash_refresh_token(refresh_token)
    db_token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    now = datetime.now(UTC)
    if db_token is None or db_token.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    user = db_token.user
    if not user.is_active or not user.is_manager:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user.")

    db_token.revoked_at = now
    db.commit()
    db.refresh(user)
    return _issue_session(db, user)


def logout(db: Session, refresh_token: str | None) -> None:
    if not refresh_token:
        return
    token_hash = hash_refresh_token(refresh_token)
    db_token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if db_token is not None and db_token.revoked_at is None:
        db_token.revoked_at = datetime.now(UTC)
        db.commit()
