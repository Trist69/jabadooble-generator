"""
Compute (x, y, size) positions for symbols on a circular Dobble card.

Algorithm: place symbols on concentric rings with the first symbol at centre.
All coordinates are normalised to a unit circle (radius = 1.0).
"""

from __future__ import annotations

import math


def symbol_positions(count: int) -> list[tuple[float, float, float]]:
    """
    Return (cx, cy, radius) for `count` symbols on a unit circle card.

    The first symbol goes in the centre; the rest are distributed on rings.
    Coordinates are in the range [-1, 1].
    """
    if count <= 0:
        return []

    positions: list[tuple[float, float, float]] = []

    # Centre symbol
    centre_radius = 0.18
    positions.append((0.0, 0.0, centre_radius))

    remaining = count - 1
    if remaining == 0:
        return positions

    # Distribute on up to 2 rings
    ring_configs = _ring_configs(remaining)

    ring_r = 0.55
    for n_on_ring in ring_configs:
        sym_size = _symbol_size(n_on_ring, ring_r)
        angle_offset = math.pi / n_on_ring  # rotate alternate rings
        for i in range(n_on_ring):
            angle = 2 * math.pi * i / n_on_ring + angle_offset
            cx = ring_r * math.cos(angle)
            cy = ring_r * math.sin(angle)
            positions.append((cx, cy, sym_size))
        ring_r += 0.30  # second ring sits further out — unused if 1 ring suffices

    return positions


def _ring_configs(n: int) -> list[int]:
    """Split n symbols into rings. For n ≤ 8 use one ring; otherwise two."""
    if n <= 8:
        return [n]
    # First ring: up to 6, rest on outer ring
    first = min(6, n // 2)
    return [first, n - first]


def _symbol_size(n_on_ring: int, ring_r: float) -> float:
    """Approximate symbol radius so symbols fit without overlap."""
    if n_on_ring == 0:
        return 0.2
    chord = 2 * ring_r * math.sin(math.pi / n_on_ring)
    return min(chord * 0.38, 0.22)
