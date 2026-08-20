"""Slice 1 of the `anvil --batch` plan: the batch stream itself.

These tests were written **blind**, from slice 1 of
`docs/plans/oracle/anvil-convert-batch.md` alone — the implementation was being
written in parallel by a different agent and was never read (AGENTS.md, "Who
writes the tests"). Everything asserted here comes from the plan:

- every reason string is the contract table's, character for character (R1003
  requires the batch reason to be the single-shot reason);
- every result string is the MVP plan's vetted conversion table, so no
  arithmetic is derived by hand here;
- the three `main`-driven tests at the bottom are OD-8 / R1004's measurement:
  the decode happens inside `main`, so a `StringIO` cannot observe it and the
  binary stream has to be replaced instead.

The suite is offline and deterministic: nothing here touches a clock, a random
source, a socket or the filesystem.
"""

import io
import sys

import pytest

# These two modules do not exist at the base this file was written against — the
# convert MVP has not landed its code — so mypy resolves the package to the
# installed distribution and reports the import as untyped. `unused-ignore` rides
# along so the suppression disappears by itself the moment `cli.py` and
# `convert.py` are on `mypy_path`: nothing here is silenced once they are, and
# assembly can delete the two comments outright.
from grimsverk_anvil.cli import (  # type: ignore[import-untyped, unused-ignore]
    convert_request,
    main,
    parse_batch_line,
    run_batch,
)
from grimsverk_anvil.convert import (  # type: ignore[import-untyped, unused-ignore]
    ConversionError,
)

# The replacement character a byte that is not valid UTF-8 decodes to under
# `errors="replace"`. Spelled once, so the expectations below read as the user
# would see them.
REPLACEMENT = "�"


def _run(text: str) -> tuple[str, int]:
    """Feed `text` to `run_batch` as a stream and return (standard output, code)."""
    out = io.StringIO()
    code = run_batch(io.StringIO(text), out)
    return out.getvalue(), code


class _RecordingStream(io.StringIO):
    """A stream that snapshots its whole content every time it is flushed.

    The snapshots are how the streaming property is measured: if a batch answers
    each request as it is read, the content at the k-th flush is exactly the
    output of the first k requests. Comparing snapshots rather than counting
    `write` calls keeps the test independent of whether the implementation
    writes the line and its newline together or separately.
    """

    def __init__(self) -> None:
        super().__init__()
        self.snapshots: list[str] = []

    def flush(self) -> None:
        super().flush()
        self.snapshots.append(self.getvalue())


class _StdinStub:
    """A stand-in for `sys.stdin` that carries only a binary buffer.

    `main` is required to decode standard input itself, through
    `sys.stdin.buffer`, so this is all it may rely on.
    """

    def __init__(self, data: bytes) -> None:
        self.buffer = io.BytesIO(data)


# --------------------------------------------------------------------------
# run_batch — the stream
# --------------------------------------------------------------------------


def test_two_request_happy_path() -> None:
    output, code = _run("0.1 km m\n1 mi km\n")

    assert output == "100\n1.609344\n"
    assert code == 0


def test_batch_whose_every_line_converts() -> None:
    output, code = _run(
        "0.1 km m\n1 mi km\n1 ft in\n100 cm m\n2500 mm m\n3 m cm\n1 in cm\n5000 m km\n"
        "1 lb kg\n2 lb oz\n16 oz lb\n500 g kg\n1 oz g\n2500 mg g\n"
    )

    assert output == (
        "100\n1.609344\n12\n1\n2.5\n300\n2.54\n5\n0.45359237\n32\n1\n0.5\n28.349523125\n2.5\n"
    )
    assert code == 0


def test_blank_lines_in_the_middle_and_at_the_end_produce_no_output_line() -> None:
    output, code = _run("1 ft in\n\n16 oz lb\n\n")

    assert output == "12\n1\n"
    assert code == 0


def test_whitespace_only_lines_produce_no_output_line() -> None:
    output, code = _run("   \n\t\n \t \n1 ft in\n")

    assert output == "12\n"
    assert code == 0


def test_empty_input_is_a_successful_batch_of_zero_requests() -> None:
    output, code = _run("")

    assert output == ""
    assert code == 0


def test_last_line_without_a_trailing_newline_is_still_a_request() -> None:
    output, code = _run("0.1 km m\n1 mi km")

    assert output == "100\n1.609344\n"
    assert code == 0


def test_carriage_return_from_crlf_input_is_not_part_of_the_unit() -> None:
    output, code = _run("1 ft in\r\n5000 m km\r\n")

    assert output == "12\n5\n"
    assert code == 0


def test_lines_may_be_any_iterable_of_strings() -> None:
    # The signature says `Iterable[str]`, not "a file". A plain list is the
    # cheapest thing that proves the declared type is the honest one.
    out = io.StringIO()
    code = run_batch(["0.1 km m", "1 mi km"], out)

    assert out.getvalue() == "100\n1.609344\n"
    assert code == 0


def test_a_refused_request_prints_its_reason_on_the_same_stream_and_makes_the_exit_one() -> None:
    output, code = _run("0.1 km m\n5 xyz m\n1 mi km\n")

    assert output == "100\nanvil: line 2: unknown unit: 'xyz'\n1.609344\n"
    assert code == 1


def test_line_numbers_count_blank_lines() -> None:
    # The blank is line 2 and prints nothing; the failure after it is line 3.
    output, code = _run("1 ft in\n\n5 xyz m\n")

    assert output == "12\nanvil: line 3: unknown unit: 'xyz'\n"
    assert code == 1


def test_a_malformed_line_refuses_and_the_batch_carries_on() -> None:
    output, code = _run("1 ft in\n5 km\n16 oz lb\n")

    assert output == "12\nanvil: line 2: malformed line: '5 km'\n1\n"
    assert code == 1


def test_each_request_is_written_and_flushed_before_the_next_one_is_read() -> None:
    stream = _RecordingStream()
    code = run_batch(io.StringIO("0.1 km m\n5 xyz m\n1 mi km\n"), stream)

    expected_prefixes = [
        "100\n",
        "100\nanvil: line 2: unknown unit: 'xyz'\n",
        "100\nanvil: line 2: unknown unit: 'xyz'\n1.609344\n",
    ]
    # Deduplicated, in order: an implementation that flushes twice for one
    # request is still streaming; one that flushes only at the end is not.
    seen: list[str] = []
    for snapshot in stream.snapshots:
        if snapshot and (not seen or snapshot != seen[-1]):
            seen.append(snapshot)

    assert seen == expected_prefixes
    assert stream.getvalue() == expected_prefixes[-1]
    assert code == 1


# --------------------------------------------------------------------------
# parse_batch_line — one line into three fields, or nothing, or a refusal
# --------------------------------------------------------------------------


@pytest.mark.parametrize("line", ["\n", "", "   \n", "\t\n", " \t \n", "\r\n"])
def test_parse_batch_line_returns_none_for_a_blank_line(line: str) -> None:
    assert parse_batch_line(line) is None


def test_parse_batch_line_returns_the_three_fields() -> None:
    assert parse_batch_line("0.1 km m\n") == ("0.1", "km", "m")


def test_parse_batch_line_ignores_runs_of_whitespace_around_and_between_fields() -> None:
    assert parse_batch_line("  1   mi\tkm  \n") == ("1", "mi", "km")


@pytest.mark.parametrize(
    ("line", "reason"),
    [
        ("5 km\n", "malformed line: '5 km'"),
        ("5 km mi extra\n", "malformed line: '5 km mi extra'"),
        ("5\n", "malformed line: '5'"),
        ("  5 km  \n", "malformed line: '5 km'"),
        ("5   km\n", "malformed line: '5   km'"),
    ],
)
def test_parse_batch_line_refuses_any_other_field_count(line: str, reason: str) -> None:
    # The quoted text is the line stripped of surrounding whitespace and of its
    # newline; internal spacing is left as the user typed it.
    with pytest.raises(ConversionError) as excinfo:
        parse_batch_line(line)

    assert str(excinfo.value) == reason


# --------------------------------------------------------------------------
# convert_request — the one path single-shot and batch share
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        (("0.1", "km", "m"), "100"),
        (("1", "mi", "km"), "1.609344"),
        (("1", "ft", "in"), "12"),
        (("5000", "m", "km"), "5"),
        (("2", "lb", "oz"), "32"),
        (("500", "g", "kg"), "0.5"),
        (("1", "oz", "g"), "28.349523125"),
    ],
)
def test_convert_request_returns_the_formatted_result(
    fields: tuple[str, str, str], expected: str
) -> None:
    value_text, from_unit, to_unit = fields

    assert convert_request(value_text, from_unit, to_unit) == expected


@pytest.mark.parametrize(
    ("fields", "reason"),
    [
        (("5", "xyz", "m"), "unknown unit: 'xyz'"),
        (("5", "km", "xyz"), "unknown unit: 'xyz'"),
        (("5", "kg", "m"), "cannot convert 'kg' (mass) to 'm' (length)"),
        (("abc", "km", "m"), "not a number: 'abc'"),
        (("inf", "km", "m"), "not a number: 'inf'"),
        (("1e308", "km", "mm"), "result is out of range: '1e308' km to mm"),
        ((REPLACEMENT, "km", "m"), f"not a number: '{REPLACEMENT}'"),
    ],
)
def test_convert_request_raises_the_contract_reason(
    fields: tuple[str, str, str], reason: str
) -> None:
    value_text, from_unit, to_unit = fields

    with pytest.raises(ConversionError) as excinfo:
        convert_request(value_text, from_unit, to_unit)

    assert str(excinfo.value) == reason


# --------------------------------------------------------------------------
# main --batch — R1004: a byte that is not valid UTF-8 never ends the batch
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("stdin_bytes", "expected_stdout", "expected_code"),
    [
        (
            b"\xff km m\n1 mi km\n",
            f"anvil: line 1: not a number: '{REPLACEMENT}'\n1.609344\n",
            1,
        ),
        (
            b"1 k\xffm m\n5000 m km\n",
            f"anvil: line 1: unknown unit: 'k{REPLACEMENT}m'\n5\n",
            1,
        ),
        (b"0.1 km m\n1 mi km\n", "100\n1.609344\n", 0),
    ],
)
def test_main_batch_decodes_standard_input_with_replacement(
    stdin_bytes: bytes,
    expected_stdout: str,
    expected_code: int,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # These have to go through `main`: the decode lives there, and a StringIO
    # gives nothing to decode. Replacing the binary stream is what OD-8's
    # measurement paragraph asks for.
    monkeypatch.setattr(sys, "stdin", _StdinStub(stdin_bytes))

    code = main(["--batch"])

    captured = capsys.readouterr()
    assert captured.out == expected_stdout
    assert captured.err == ""
    assert code == expected_code
