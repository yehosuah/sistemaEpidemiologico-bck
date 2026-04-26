from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


def ensure_manager(db: Session) -> User | None:
    if not settings.manager_email or not settings.manager_password:
        return None

    existing = db.scalar(select(User).where(User.email == settings.manager_email.lower()))
    if existing:
        if not existing.is_manager:
            existing.is_manager = True
            db.commit()
            db.refresh(existing)
        return existing

    user = User(
        email=settings.manager_email.lower(),
        password_hash=hash_password(settings.manager_password),
        is_manager=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
