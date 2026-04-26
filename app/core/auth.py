from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.services.users import get_user

bearer_scheme = HTTPBearer(auto_error=False)


def _credentials_from_request(
    request: Request,
    bearer: HTTPAuthorizationCredentials | None,
) -> str | None:
    if bearer and bearer.scheme.lower() == "bearer":
        return bearer.credentials
    cookie_token = request.cookies.get(settings.access_cookie_name)
    if cookie_token:
        return cookie_token
    return None


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User | None:
    token = _credentials_from_request(request, bearer)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
    except ValueError:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None
    user = get_user(db, user_id)
    if user is None or not user.is_active:
        return None
    return user


def get_current_user(
    user: User | None = Depends(get_optional_current_user),
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return user


def require_manager() -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager access required.",
            )
        return current_user

    return dependency
