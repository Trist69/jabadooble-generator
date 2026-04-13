from __future__ import annotations

from uuid import UUID, uuid4
from pydantic import BaseModel, field_validator


class SymbolPlacement(BaseModel):
    label: str
    url: str
    cx: float   # normalised [-1, 1]
    cy: float
    size: float  # normalised radius


class GameCard(BaseModel):
    index: int
    placements: list[SymbolPlacement]


class Game(BaseModel):
    id: UUID = uuid4()
    library_id: str
    order: int
    total_cards: int
    cards: list[GameCard]

    @field_validator("id", mode="before")
    @classmethod
    def coerce_uuid(cls, v: object) -> UUID:
        return UUID(str(v)) if not isinstance(v, UUID) else v


class GameGenerateRequest(BaseModel):
    library_id: str
    order: int = 7
