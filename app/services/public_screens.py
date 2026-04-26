from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.public_screen import PublicScreen
from app.schemas.public_screen import PublicScreenCreate, PublicScreenUpdate


def list_enabled_screens(db: Session) -> list[PublicScreen]:
    return list(
        db.scalars(
            select(PublicScreen)
            .where(PublicScreen.enabled.is_(True))
            .order_by(PublicScreen.display_order, PublicScreen.key)
        )
    )


def list_all_screens(db: Session) -> list[PublicScreen]:
    return list(db.scalars(select(PublicScreen).order_by(PublicScreen.display_order, PublicScreen.key)))


def create_screen(db: Session, payload: PublicScreenCreate) -> PublicScreen:
    existing = db.get(PublicScreen, payload.key)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Screen already exists.")

    screen = PublicScreen(
        key=payload.key,
        title=payload.title,
        enabled=payload.enabled,
        display_order=payload.display_order,
    )
    db.add(screen)
    db.commit()
    db.refresh(screen)
    return screen


def update_screen(db: Session, key: str, payload: PublicScreenUpdate) -> PublicScreen:
    screen = db.get(PublicScreen, key)
    if screen is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screen not found.")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(screen, field, value)
    db.commit()
    db.refresh(screen)
    return screen
