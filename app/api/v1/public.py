from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.public_screen import PublicScreenRead
from app.services import public_screens

router = APIRouter()


@router.get("/screens", response_model=list[PublicScreenRead])
def list_public_screens(db: Session = Depends(get_db)):
    return public_screens.list_enabled_screens(db)
