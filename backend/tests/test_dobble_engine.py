"""Tests for the Dobble projective-plane card matrix generator."""

import pytest
from app.core.dobble_engine import generate_card_matrix, total_cards, symbols_per_card


@pytest.mark.parametrize("order", [2, 3, 5, 7])
def test_correct_card_count(order: int) -> None:
    cards = generate_card_matrix(order)
    assert len(cards) == total_cards(order)


@pytest.mark.parametrize("order", [2, 3, 5, 7])
def test_correct_symbols_per_card(order: int) -> None:
    cards = generate_card_matrix(order)
    n = symbols_per_card(order)
    for i, card in enumerate(cards):
        assert len(card) == n, f"Card {i} has {len(card)} symbols, expected {n}"


@pytest.mark.parametrize("order", [2, 3, 5, 7])
def test_any_two_cards_share_exactly_one_symbol(order: int) -> None:
    cards = generate_card_matrix(order)
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            shared = set(cards[i]) & set(cards[j])
            assert len(shared) == 1, (
                f"Cards {i} and {j} share {len(shared)} symbols: "
                f"{cards[i]} ∩ {cards[j]} = {shared}"
            )


@pytest.mark.parametrize("order", [2, 3, 5, 7])
def test_all_symbols_used(order: int) -> None:
    cards = generate_card_matrix(order)
    used = {sym for card in cards for sym in card}
    expected = set(range(total_cards(order)))
    assert used == expected


@pytest.mark.parametrize("order", [2, 3, 5, 7])
def test_no_duplicate_symbols_within_card(order: int) -> None:
    cards = generate_card_matrix(order)
    for i, card in enumerate(cards):
        assert len(card) == len(set(card)), f"Card {i} has duplicate symbols: {card}"


def test_standard_dobble_shape() -> None:
    """Standard Dobble uses order 7: 57 cards, 8 symbols each."""
    cards = generate_card_matrix(7)
    assert len(cards) == 57
    assert all(len(c) == 8 for c in cards)


def test_invalid_order_raises() -> None:
    with pytest.raises(ValueError):
        generate_card_matrix(4)  # 4 is not prime

    with pytest.raises(ValueError):
        generate_card_matrix(1)

    with pytest.raises(ValueError):
        generate_card_matrix(0)
