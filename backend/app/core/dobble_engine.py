"""
Dobble engine — projective plane card matrix generator.

For a prime order n the construction produces:
  • n² + n + 1 cards
  • n + 1 symbols per card
  • Any two cards share exactly one symbol

Algorithm: finite projective plane PG(2, n) over GF(n) (n prime).
"""

from __future__ import annotations


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def generate_card_matrix(order: int) -> list[list[int]]:
    """
    Generate a Dobble card matrix for a prime order n.

    Returns a list of n²+n+1 cards.  Each card is a sorted list of n+1
    symbol indices (0-based, range 0 … n²+n).

    Raises:
        ValueError: if order is not a prime ≥ 2.
    """
    n = order

    if n < 2 or not _is_prime(n):
        raise ValueError(f"Order must be a prime number ≥ 2, got {n}")

    cards: list[list[int]] = []

    # ── Line at infinity ────────────────────────────────────────────────
    # Symbols 0 … n:  one "infinity point" per slope + one extra
    cards.append(list(range(n + 1)))

    # ── n vertical cards ────────────────────────────────────────────────
    # Each connects to infinity symbol 0 and contains a column of the grid
    for i in range(n):
        card = [0] + [n + 1 + i * n + j for j in range(n)]
        cards.append(card)

    # ── n² affine cards ─────────────────────────────────────────────────
    # For each slope s ∈ GF(n) and intercept b ∈ GF(n):
    #   card = { infinity_symbol(s+1) } ∪ { grid symbol (x, (s*x+b) mod n) }
    for slope in range(n):
        for intercept in range(n):
            card = [1 + slope]
            for x in range(n):
                y = (slope * x + intercept) % n
                card.append(n + 1 + x * n + y)
            cards.append(card)

    return [sorted(c) for c in cards]


def total_cards(order: int) -> int:
    return order * order + order + 1


def symbols_per_card(order: int) -> int:
    return order + 1
