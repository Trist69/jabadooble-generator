from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.core.dobble_engine import generate_card_matrix
from app.core.card_layout import symbol_positions
from app.core import storage
from app.models.game import Game, GameCard, GameGenerateRequest, SymbolPlacement
from app.services import library_service, pdf_service

router = APIRouter(prefix="/games", tags=["games"])

COLLECTION = "games"


@router.post("", response_model=Game, status_code=201)
async def generate_game(req: GameGenerateRequest) -> Game:
    """Generate a Dobble game from a library and save it."""
    lib = library_service.get_library(req.library_id)
    if lib is None:
        raise HTTPException(status_code=404, detail="Library not found")

    n = req.order
    required = n * n + n + 1
    if len(lib.symbols) < required:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Library needs at least {required} symbols for order {n}, "
                f"has {len(lib.symbols)}"
            ),
        )

    try:
        matrix = generate_card_matrix(n)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    positions = symbol_positions(n + 1)
    cards: list[GameCard] = []

    for card_index, symbol_indices in enumerate(matrix):
        placements: list[SymbolPlacement] = []
        for pos_index, sym_index in enumerate(symbol_indices):
            sym = lib.symbols[sym_index]
            cx, cy, size = positions[pos_index] if pos_index < len(positions) else (0.0, 0.0, 0.15)
            url = sym.cartoonized_url or sym.url
            placements.append(
                SymbolPlacement(label=sym.label, url=url, cx=cx, cy=cy, size=size)
            )
        cards.append(GameCard(index=card_index, placements=placements))

    game = Game(
        id=uuid4(),
        library_id=req.library_id,
        order=n,
        total_cards=len(cards),
        cards=cards,
    )
    storage.put(COLLECTION, str(game.id), game.model_dump())
    return game


@router.get("", response_model=list[Game])
async def list_games() -> list[Game]:
    return [Game(**raw) for raw in storage.all_values(COLLECTION)]


@router.get("/{game_id}", response_model=Game)
async def get_game(game_id: str) -> Game:
    raw = storage.get(COLLECTION, game_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return Game(**raw)


@router.delete("/{game_id}", status_code=204)
async def delete_game(game_id: str) -> None:
    if not storage.delete(COLLECTION, game_id):
        raise HTTPException(status_code=404, detail="Game not found")


@router.get("/{game_id}/export/pdf")
async def export_pdf(game_id: str) -> Response:
    """Export the game as a print-ready PDF (2 cards per A4 page)."""
    raw = storage.get(COLLECTION, game_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="Game not found")
    game = Game(**raw)

    # Limit to reasonable number of cards to prevent huge PDFs
    max_cards = 20  # Limit to 10 pages max
    if len(game.cards) > max_cards:
        game.cards = game.cards[:max_cards]
        game.total_cards = max_cards

    try:
        pdf_bytes = pdf_service.generate_pdf(game)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}") from exc

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="dobble-{game_id[:8]}.pdf"'},
    )
