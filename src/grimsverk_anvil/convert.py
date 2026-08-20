"""Conversion through the category's base unit, and the R1000 result format."""

from __future__ import annotations

from grimsverk_anvil.units import lookup


class ConversionError(Exception):
    """A request that cannot be converted; str(exc) is the user-facing reason."""


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert through the category's base unit."""
    source = lookup(from_unit)
    if source is None:
        raise ConversionError(f"unknown unit: '{from_unit}'")
    target = lookup(to_unit)
    if target is None:
        raise ConversionError(f"unknown unit: '{to_unit}'")
    if source.category != target.category:
        raise ConversionError(
            f"cannot convert '{from_unit}' ({source.category}) to '{to_unit}' ({target.category})"
        )
    return value * source.to_base / target.to_base


def format_result(value: float) -> str:
    """R1000: every printed result is `format(value, ".12g")`."""
    return format(value, ".12g")
