"""The `anvil` command line tool.

Single-shot conversion (`anvil <value> <from-unit> <to-unit>`) and batch mode
(`anvil --batch`), which reads one request per line from standard input.
"""

from __future__ import annotations

import io
import math
import sys
from collections.abc import Iterable, Sequence
from typing import TextIO

from grimsverk_anvil.convert import ConversionError, convert, format_result


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
