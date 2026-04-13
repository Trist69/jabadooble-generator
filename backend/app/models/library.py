from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, HttpUrl, field_validator


class Symbol(BaseModel):
    id: UUID = uuid4()
    label: str
    url: str
    thumbnail_url: str | None = None
    cartoonized_url: str | None = None
    cartoonized: bool = False

    @field_validator("id", mode="before")
    @classmethod
    def coerce_uuid(cls, v: object) -> UUID:
        return UUID(str(v)) if not isinstance(v, UUID) else v


class SymbolCreate(BaseModel):
    label: str
    url: str


class Library(BaseModel):
    id: UUID = uuid4()
    name: str
    theme: str
    symbols: list[Symbol] = []

    @field_validator("id", mode="before")
    @classmethod
    def coerce_uuid(cls, v: object) -> UUID:
        return UUID(str(v)) if not isinstance(v, UUID) else v


class LibraryCreate(BaseModel):
    name: str
    theme: str
    symbols: list[SymbolCreate]
