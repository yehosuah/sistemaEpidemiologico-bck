from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import require_manager
from app.db.session import get_db
from app.schemas.public_screen import PublicScreenCreate, PublicScreenRead, PublicScreenUpdate
from app.services import public_screens

router = APIRouter(dependencies=[Depends(require_manager())])


@router.get("/screens", response_model=list[PublicScreenRead])
def list_screens(db: Session = Depends(get_db)):
    return public_screens.list_all_screens(db)


@router.post("/screens", response_model=PublicScreenRead, status_code=status.HTTP_201_CREATED)
def create_screen(
    payload: PublicScreenCreate,
    db: Session = Depends(get_db),
):
    return public_screens.create_screen(db, payload)


@router.patch("/screens/{key}", response_model=PublicScreenRead)
def update_screen(
    key: str,
    payload: PublicScreenUpdate,
    db: Session = Depends(get_db),
):
    return public_screens.update_screen(db, key, payload)
