from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PublicScreenRead(BaseModel):
    key: str
    title: str
    enabled: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicScreenCreate(BaseModel):
    key: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,79}$")
    title: str = Field(min_length=1, max_length=160)
    enabled: bool = True
    display_order: int = 0


class PublicScreenUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    enabled: bool | None = None
    display_order: int | None = None
