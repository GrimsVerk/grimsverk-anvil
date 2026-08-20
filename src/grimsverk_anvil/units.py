"""The unit table: every known symbol, its category, and its factor to base."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Unit:
    symbol: str
    category: str  # "length" or "mass"
    to_base: float  # multiply by this to reach the category's base unit


# Base unit metre for length, gram for mass. Every factor is the exact
# international definition, not a rounded one.
UNITS: dict[str, Unit] = {
    "m": Unit("m", "length", 1.0),
    "km": Unit("km", "length", 1000.0),
    "cm": Unit("cm", "length", 0.01),
    "mm": Unit("mm", "length", 0.001),
    "mi": Unit("mi", "length", 1609.344),
    "ft": Unit("ft", "length", 0.3048),
    "in": Unit("in", "length", 0.0254),
    "g": Unit("g", "mass", 1.0),
    "kg": Unit("kg", "mass", 1000.0),
    "mg": Unit("mg", "mass", 0.001),
    "lb": Unit("lb", "mass", 453.59237),
    "oz": Unit("oz", "mass", 28.349523125),
}


def lookup(symbol: str) -> Unit | None:
    """Return the unit for an exact symbol match, or None."""
    return UNITS.get(symbol)
