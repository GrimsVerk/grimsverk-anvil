---
slug: od5-convert-cli       # MUST appear in every branch name working this plan
status: draft               # draft | in-flight | merged
created: 2026-08-20
design: MVP milestone `convert` (docs/DESIGN.md §12) — its conversion core, its CLI layer, and its two acceptance scripts
covers: [R1, R2, R4, R5, R7, R8, R1001, R1002]
---

# The `convert` milestone — single-shot conversions (OD-5 / OD-6 / OD-7) — Plan

## Summary

**What this builds.** The MVP `convert` milestone: the installed `anvil`
command converts length and mass, prints one number, refuses bad input by name,
and two acceptance scripts check both halves on every pull request. Three
decisions unblock it — `OD-5` (**R1001**, the command line), `OD-6` (**R1002**,
the output contract), `OD-7` (R7 and R8 belong to this milestone). `covers:`
is `[R1, R2, R4, R5, R7, R8, R1001, R1002]`, exactly as `OD-7` and this run's
handoff direct.

**Decisions worth saying no to.**

- **Every failure exits `1`.** R4 and R5 require "non-zero" and §4's script
  author needs only success versus failure; one code is the smallest rule that
  satisfies both. No separate usage code.
- **Argument parsing is hand-rolled, not `argparse`.** `argparse` brings its
  own usage text, its own exit code and a `-h` flag nobody asked for, and
  R1002 fixes exactly which stream carries what. ~15 lines of `sys.argv`
  handling keeps the contract literal.
- **A token is a flag if it starts with `-` and does not parse as a number.**
  So `anvil -5 km mi` converts, and `anvil --batch` is the usage error R1001
  reserves it as until R6 is built.
- **Three error messages are fixed here** — `not a number: '<x>'`,
  `unknown unit: '<x>'`, `cannot convert <cat> to <cat>: '<x>' and '<y>'` —
  each naming the offending input (R4). Nothing in the design fixes the words.
- **The print point uses `format(value, ".12g")` literally**, because R1002
  says the output line *is* that expression. A side effect worth stating: the
  `ESC-1` case (`0.1 km` in `m`) therefore prints `100` as soon as this
  milestone lands, before `od1-output-precision` builds. That plan keeps its
  own work and its own place after this one — see "Existing plans" below.
- **Four slices, split at module seams.** Slice workers build in parallel
  worktrees, so two slices must not share a file; `docs/architecture.md` is
  therefore updated once, in the last slice, for the whole milestone.

**Deliberately not done.** Temperature (R3) and batch (R6) — later milestones.
Aliases (`BL-1`) and sub-zero inputs (`BL-2`) — unruled, so unplannable.
`docs/acceptance.md` rows — the acceptance pass writes those. The `ESC-1`
acceptance row, the shared `format_result` function and the ledger closure —
`od1-output-precision`'s, untouched here.

**What it costs you.** No dependency, no gate change, nothing to run by hand.
`pyproject.toml` gains a `[project.scripts]` entry point (R7). Two new
acceptance scripts, `S1` and `S3`, then run on **every** future pull request —
they will turn a pull request red if the CLI's output or its refusals change,
which is what `OD-5` and `OD-6` named as their measurement.

**Open questions.** One, LOW, filed as `BL-9` and proceeded on: whether the
spellings `nan` and `inf`, which Python's `float()` accepts, count as "a value
that is not a number" under R4. Default taken: they do — rejected with the
same named error as `five`.

## Uncertainties

- **Q:** R4 makes "a value that is not a number" an error, and §6 assumes
  integer and decimal inputs. `float()` also accepts `nan`, `inf`, `-inf` and
  `1e400` (which becomes `inf`). Does R4 cover those, or do they convert? —
  **risk:** LOW — it is one guard inside `parse_value`, which already raises
  this exact error type; no signature, slice boundary, external format or S1/S3
  case changes on either answer, and reversing it is two lines and one test —
  **proposed:** reject them. A result of `nan` or `inf` is a number-shaped
  answer that means nothing, and R4's error already names the offending input.
  **Ruling:** filed as `BL-9` in `docs/BACKLOG.md`; proceeded on the default
  (LOW), left for the oracle's next cycle.

### Derivations, recorded here rather than filed

Answered by the design layer. Each names what answered it.

- **The command line.** R1001 (`OD-5`): exactly three positionals, in the order
  value, from-unit, to-unit; no subcommand; a bare `anvil`, a wrong count,
  `--batch`, or any unrecognised flag is a usage error under R5; `--batch` is
  reserved, not delivered, until R6.
- **The output.** R1002 (`OD-6`): one line on standard output, the formatted
  value alone, no unit suffix and no echo; errors and usage on standard error;
  nothing on standard output when the invocation fails.
- **Unit spelling.** R1001 pins the §5 symbols, matched exactly and
  case-sensitively, *because* `BL-1` (aliases) is unruled. `KM` is an unknown
  unit today, and that is deliberate.
- **`covers:` including R7 and R8.** `OD-7` rules it: this milestone is where
  the installed console command and the stdlib-only runtime first exist.
- **Conversion shape.** §8 chooses a base-unit hub and §9 gives the table its
  shape; §7 splits table, converter and a thin CLI. Base units are metre and
  gram (§8); kelvin waits for the `temperature` milestone.
- **Build order against `od1-output-precision`.** That plan says in its own
  summary that it builds after this milestone's work, and `OD-1` places R1000
  in this milestone's print layer. This plan is first.
- **Module and function names, and the error wording.** Not fixed anywhere in
  the design layer, which delegates the plan's own program design; chosen in
  the Signatures blocks below. `cli.py` and a `main()` entry point are chosen
  to match what `od1-output-precision` already assumes it will edit.

## The slices

Each slice owns its files outright. Workers build slices in parallel worktrees
off the same base (`.claude/orchestration.md`), so a file named by two slices is
a merge conflict by construction; that is why the seam between slice 1 and slice
2 is the module boundary §7 already draws, and why the architecture doc is
written once at the end.

## Slice 1 — the converter answers, and refuses by name

- **Delivers:** the conversion core, observable on its own —
  `uv run python -c "from grimsverk_anvil.convert import convert; print(convert(5, 'km', 'mi'))"`
  prints the miles, and an unknown unit, a cross-category pair or a non-numeric
  value each raises a distinct error whose text names the offending input.
- **Files:** `src/grimsverk_anvil/units.py`, `src/grimsverk_anvil/convert.py`, `tests/test_units.py`, `tests/test_convert.py`
- **Estimate:** ~205 lines

### Signatures

```python
Category = Literal["length", "mass"]


@dataclass(frozen=True)
class Unit:
    symbol: str
    category: Category
    to_base: float


UNITS: dict[str, Unit]


class AnvilError(Exception): ...


class NotANumberError(AnvilError):
    def __init__(self, text: str) -> None: ...


class UnknownUnitError(AnvilError):
    def __init__(self, symbol: str) -> None: ...


class CategoryMismatchError(AnvilError):
    def __init__(self, source: Unit, target: Unit) -> None: ...


def parse_value(text: str) -> float: ...
def convert(value: float, from_symbol: str, to_symbol: str) -> float: ...
```

The contract, for the test author and the coder alike:

- `UNITS` is keyed by the §5 symbols exactly, case-sensitively, and by nothing
  else: `m`, `km`, `cm`, `mm`, `mi`, `ft`, `in` in category `length`, base
  metre; `kg`, `g`, `mg`, `lb`, `oz` in category `mass`, base gram. `to_base`
  is the multiplier to that base: `km` 1000, `cm` 0.01, `mm` 0.001, `mi`
  1609.344, `ft` 0.3048, `in` 0.0254, `m` 1; `kg` 1000, `g` 1, `mg` 0.001,
  `lb` 453.59237, `oz` 28.349523125. Twelve entries, no more.
- `parse_value(text)` returns `float(text)`, and raises `NotANumberError(text)`
  when `float()` refuses it **or** when the result is not finite (`nan`, `inf`,
  `-inf`, and overflowing literals such as `1e400`). This is the `BL-9`
  default.
- `convert(value, from_symbol, to_symbol)` looks up both symbols and returns
  `value * source.to_base / target.to_base`. It raises `UnknownUnitError` for
  the first symbol not in `UNITS`, checking `from_symbol` before `to_symbol`;
  `CategoryMismatchError(source, target)` when both exist but their categories
  differ. It does no rounding — R1000/R1002 apply where the value is printed.
- `str()` of each error is the message the CLI prints, and each names the
  offending input: `not a number: 'five'`; `unknown unit: 'parsec'`;
  `cannot convert mass to length: 'kg' and 'm'`.
- Same-unit conversion is legal and returns the value unchanged.

## Slice 2 — the installed `anvil` command

- **Delivers:** `anvil 5 km mi` prints `3.10685596119` and exits 0; every
  malformed invocation prints to standard error, leaves standard output empty,
  and exits 1. The console command exists (R7) and the package still declares
  no runtime dependency (R8).
- **Files:** `pyproject.toml`, `src/grimsverk_anvil/cli.py`, `tests/test_cli.py`
- **Estimate:** ~150 lines

### Signatures

```python
USAGE = "usage: anvil <value> <from-unit> <to-unit>"


def main(argv: list[str] | None = None) -> int: ...
```

The contract:

- `pyproject.toml` gains `[project.scripts]` with
  `anvil = "grimsverk_anvil.cli:main"` — the wrapper uses the return value as
  the exit status, so `main` returns an `int` and never calls `sys.exit`.
  Nothing else in `pyproject.toml` changes; no dependency is added. If
  `uv sync --locked` then reports the lock as stale, refresh `uv.lock` in the
  same commit and say so in the pull request body (`AGENTS.md`, Dependencies).
- `main(None)` reads `sys.argv[1:]`; tests pass a list.
- **Flag rule:** a token is a flag when it starts with `-` and `parse_value`
  rejects it. If any token is a flag — `--batch` included, per R1001 —
  `main` writes `USAGE` to standard error and returns 1.
- Otherwise, if there are not exactly three tokens (zero included: the bare
  `anvil`), it writes `USAGE` to standard error and returns 1.
- Otherwise it calls `parse_value` then `convert`, and on `AnvilError` writes
  `str(err)` to standard error and returns 1.
- On success it writes `format(result, ".12g")` and a newline to standard
  output — the whole line, nothing else, per R1002 — and returns 0.
- Standard output stays empty on every failure path; standard error stays empty
  on success.
- Worked strings for the test author: `["5", "km", "mi"]` → `3.10685596119`;
  `["100", "cm", "m"]` → `1`; `["1", "mg", "kg"]` → `1e-06`; `["-5", "km",
  "m"]` → `-5000` (a negative value is not a flag). Where a string here
  disagrees with `format(value, ".12g")`, **the expression is the contract**
  and the string is wrong.

## Slice 3 — S1 checks ten conversions on every pull request

- **Delivers:** `acceptance/S1.sh`, the executable form of §13's S1 (R1, R2).
  It runs the installed command over a fixed table and compares the **entire**
  standard-output line against each expected value — `OD-6`'s measurement
  obligation.
- **Files:** `acceptance/S1.sh`
- **Estimate:** ~45 lines

### Signatures

No Python. The script's contract is `acceptance/README.md`'s: exit 0 is pass,
standard output is the evidence, `set -euo pipefail`, offline, and it prints
what it measured rather than a verdict. It invokes the **installed** command —
`uv run --frozen anvil …` — never `python -m` and never an import, because S1
says "through the installed `anvil` command".

The table, twelve rows (S1 asks for at least ten), each `value from to` with the
exact expected line:

    5 km mi     3.10685596119
    1 mi km     1.609344
    100 cm m    1
    1 m mm      1000
    12 in ft    1
    3 ft in     36
    0.5 mi ft   2640
    1 kg g      1000
    16 oz lb    1
    1 lb g      453.59237
    500 mg g    0.5
    1 mg kg     1e-06

The comparison is string equality against the whole line. Where a row here
disagrees with `format(value, ".12g")` of the true conversion, the expression
wins and the row is corrected — record the observed output in the commit
message when that happens. The `0.1 km` → `m` row is deliberately absent: it is
`ESC-1`'s case and belongs to `od1-output-precision`, which adds it.

## Slice 4 — S3 checks every refusal, and the architecture doc catches up

- **Delivers:** `acceptance/S3.sh`, the executable form of §13's S3 (R4, R5),
  asserting for every failure case that the exit status is non-zero, that
  standard error carries a message naming the offending input, and that
  standard output is **empty** — `OD-6`'s second measurement obligation. Plus
  `docs/architecture.md` describing the milestone as built.
- **Files:** `acceptance/S3.sh`, `docs/architecture.md`
- **Estimate:** ~70 lines

### Signatures

No Python. Same script contract as slice 3, same `uv run --frozen anvil`
invocation. Seven cases:

| invocation | what is asserted on standard error |
| --- | --- |
| `anvil 5 km parsec` | names `parsec` |
| `anvil 5 kg m` | names `kg` and `m` |
| `anvil five km mi` | names `five` |
| `anvil` | usage text (R5, and R1001's bare-invocation ruling) |
| `anvil 5 km` | usage text |
| `anvil 5 km mi extra` | usage text |
| `anvil --batch` | usage text (R1001 reserves the flag until R6) |

Every case also asserts a non-zero exit and empty standard output.

`docs/architecture.md` gains three components — the unit table, the converter,
the CLI — the data flow between them, and the two main paths (a successful
conversion, and a refusal), at the level of logic rather than code.

## Out of scope

- **Temperature (R3)** — milestone `temperature`. No kelvin base unit, no
  affine handling, no `C`/`F`/`K` symbols in the table.
- **Batch mode (R6)** — milestone `convert-batch`. `--batch` is a usage error
  here, exactly as R1001 requires until R6 is built. That milestone also
  inherits three obligations recorded in `OD-4` and `OD-5`, and must file the
  batch line format as its own uncertainty; none of that is this plan's.
- **R1000's shared formatting function, the `ESC-1` acceptance row, and the
  `ESC-1` ledger closure** — `docs/plans/oracle/od1-output-precision.md`,
  which builds after this plan.
- **`BL-1` (aliases) and `BL-2` (below absolute zero)** — unruled; no decision
  cites them. `BL-3` is halted by `OD-2`, `BL-4` rejected by `OD-3`.
- **`docs/acceptance.md`** — written by the acceptance pass, owner-reviewed.
  Nothing here claims a criterion passed.
- **`docs/DESIGN.md` §11's open questions** other than the two `OD-5` and
  `OD-6` closed. The batch line format stays open.
