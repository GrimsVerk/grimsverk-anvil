"""The `anvil` command line tool.

Single-shot conversion (`anvil <value> <from-unit> <to-unit>`) and batch mode
(`anvil --batch`), which reads one request per line from standard input.
"""

from __future__ import annotations

import io
import math
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import TextIO


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


def usage() -> str:
    """The usage text, without a trailing newline."""
    return "usage: anvil <value> <from-unit> <to-unit>"


def convert_request(value_text: str, from_unit: str, to_unit: str) -> str:
    """Parse, convert and format one request; the path both modes share.

    Raises ConversionError, whose str() is the user-facing reason, for every
    refusal.
    """
    try:
        value = float(value_text)
    except ValueError:
        raise ConversionError(f"not a number: '{value_text}'") from None
    # R1002: a non-finite input is refused rather than printed.
    if not math.isfinite(value):
        raise ConversionError(f"not a number: '{value_text}'")
    result = convert(value, from_unit, to_unit)
    # R1002: finite inputs whose conversion overflows are refused too.
    if not math.isfinite(result):
        raise ConversionError(f"result is out of range: '{value_text}' {from_unit} to {to_unit}")
    return format_result(result)


def parse_batch_line(line: str) -> tuple[str, str, str] | None:
    """Split one batch line into its three fields.

    Returns None for a blank or whitespace-only line. `str.split()` splits on
    runs of whitespace, so a trailing `\\r` from CRLF input goes with it.
    """
    fields = line.split()
    if not fields:
        return None
    if len(fields) != 3:
        raise ConversionError(f"malformed line: '{line.strip()}'")
    return fields[0], fields[1], fields[2]


def run_batch(lines: Iterable[str], out: TextIO) -> int:
    """Answer every request on `lines`, one output line each, as they arrive.

    Returns 1 if any request failed, 0 otherwise.
    """
    failed = False
    for number, line in enumerate(lines, start=1):
        try:
            fields = parse_batch_line(line)
            if fields is None:
                continue
            text = convert_request(*fields)
        except ConversionError as exc:
            text = f"anvil: line {number}: {exc}"
            failed = True
        out.write(text + "\n")
        out.flush()
    return 1 if failed else 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the tool and return its exit code."""
    args = list(sys.argv[1:] if argv is None else argv)

    if args == ["--batch"]:
        # R1004: decode standard input ourselves with errors="replace", so a
        # byte that is not valid UTF-8 becomes U+FFFD and its line refuses
        # through an ordinary reason instead of ending the batch.
        stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
        return run_batch(stream, sys.stdout)

    if len(args) != 3:
        print(usage(), file=sys.stderr)
        return 2

    try:
        print(convert_request(args[0], args[1], args[2]))
    except ConversionError as exc:
        print(f"anvil: {exc}", file=sys.stderr)
        return 1
    return 0
