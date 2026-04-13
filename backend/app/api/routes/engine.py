from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.dobble_engine import generate_card_matrix, total_cards, symbols_per_card

router = APIRouter(prefix="/engine", tags=["engine"])


class CardMatrixResponse(BaseModel):
    order: int
    total_cards: int
    symbols_per_card: int
    cards: list[list[int]]


@router.get("/generate", response_model=CardMatrixResponse)
async def generate(order: int = 7) -> CardMatrixResponse:
    """
    Generate a Dobble card matrix for the given prime order.
    Default order=7 → standard Dobble (57 cards, 8 symbols each).
    """
    try:
        cards = generate_card_matrix(order)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return CardMatrixResponse(
        order=order,
        total_cards=total_cards(order),
        symbols_per_card=symbols_per_card(order),
        cards=cards,
    )
