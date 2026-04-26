from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RefreshRequest
from app.schemas.user import UserRead
from app.services import auth as auth_service

router = APIRouter()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    cookie_args = {
        "httponly": True,
        "secure": settings.cookie_secure,
        "samesite": "lax",
        "domain": settings.cookie_domain,
    }
    response.set_cookie(
        settings.access_cookie_name,
        access_token,
        max_age=settings.access_token_ttl_minutes * 60,
        **cookie_args,
    )
    response.set_cookie(
        settings.refresh_cookie_name,
        refresh_token,
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
        **cookie_args,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.access_cookie_name, domain=settings.cookie_domain)
    response.delete_cookie(settings.refresh_cookie_name, domain=settings.cookie_domain)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    auth_payload = auth_service.login(db, request.email, request.password)
    _set_auth_cookies(response, auth_payload.access_token, auth_payload.refresh_token)
    return auth_payload


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    request: RefreshRequest,
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    refresh_token = request.refresh_token or http_request.cookies.get(settings.refresh_cookie_name)
    auth_payload = auth_service.refresh_session(db, refresh_token)
    _set_auth_cookies(response, auth_payload.access_token, auth_payload.refresh_token)
    return auth_payload


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: RefreshRequest,
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> None:
    refresh_token = request.refresh_token or http_request.cookies.get(settings.refresh_cookie_name)
    auth_service.logout(db, refresh_token)
    _clear_auth_cookies(response)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
