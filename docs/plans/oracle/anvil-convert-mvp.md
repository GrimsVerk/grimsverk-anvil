---
slug: anvil-convert-mvp     # MUST appear in every branch name working this plan
status: draft               # draft | in-flight | merged
created: 2026-08-20
design: MVP — milestone `convert` (docs/DESIGN.md §12)
covers: [R1, R2, R4, R5, R1000, R1001, R1002]
---

# The `anvil` convert MVP — Plan

## Summary

**What this builds.** The `anvil` command line tool, milestone `convert`: a
single-shot conversion between length and mass units, printed under the output
precision rule, with loud refusals on bad input. It implements **OD-1 / R1000**
(the precision rule that resolves ESC-1), **OD-4 / R1001** (the invocation
syntax that resolves BL-5) and **OD-5 / R1002** (non-finite values are refused,
which resolves BL-6), and it delivers the design's R1, R2, R4 and R5.

**Why this plan is the milestone plan and not an R1000-only plan.** OD-1 says
so: *"the plan covering the MVP `convert` milestone must list R1000 in its
`covers`"*, and its measurement paragraph requires the S1 acceptance script,
which runs through the installed `anvil` command. BL-5 — filed by the previous
steward on this same decision — says the same thing, and OD-4 was written to
unblock this exact plan. A plan for R1000 alone would be a formatting function
with nothing to format: a horizontal layer, which `AGENTS.md` forbids.

**Decisions that are expensive to reverse.**

- Three modules — `units.py` (the table), `convert.py` (conversion + the R1000
  formatter), `cli.py` (argument shapes, printing, exit codes). Temperature and
  batch mode extend the same three; neither needs a fourth.
- Argument parsing is **hand-rolled, not `argparse`**. R1001 requires every
  non-conforming invocation to print usage to *standard error* and exit
  *non-zero*; `argparse` answers `-h` on standard output with exit 0.
  Consequence: **this tool has no `--help`**, by R1001.
- Exit codes: **2** for a wrong argument shape (R5), **1** for a refused
  conversion (R4). R4 and R5 require only "non-zero"; this splits them so a
  script can tell a typo from a bad unit.
- Unit symbols match **exactly** — `KM` is an unknown unit, not `km`. Aliases
  and casing are BL-1, owner-filed and not commissioned.
- **R1002:** `inf`, `-inf` and `nan` inputs, and finite inputs whose conversion
  overflows, are refused on the R4 path (exit 1) rather than printed. The tool
  therefore never prints `inf` or `nan` as a result. `anvil 1e308 km mm` is an
  error, not a number.
- Conversion factors are the exact international definitions (1 mi = 1609.344 m,
  1 lb = 453.59237 g, and so on), pinned in the body.

**What it costs you.**

- `pyproject.toml` gains `[project.scripts] anvil = ...`. No dependency is
  added; V5 holds.
- Two new required-check scripts, `acceptance/S1.sh` and `acceptance/S3.sh`,
  which then run on **every** pull request from here on.
- R1000 prints large and small results in exponent form — `1e+13`, `1e-05` —
  because that is what `format(value, ".12g")` does. If you dislike that, it is
  a new decision, not a plan change.

**Deliberately not done.** Temperature (R3) and batch mode (R6) — later
milestones. `--batch` is an unrecognised argument here and takes the usage-error
path, exactly as OD-4 says. Unit aliases (BL-1), absolute-zero checks (BL-2),
pretty output (BL-3, halted). The ESC-1 correction row is **not** in this plan:
`AGENTS.md` forbids a change carrying its own ledger entry, so it lands as a
one-line `docs/` pull request after this work merges.

**Open questions.** None. The one this plan carried — **BL-6**, non-finite
values — has since been ruled: **OD-5 / R1002** confirms the default taken here,
so no code direction changes and `acceptance/S3.sh` gains the two rows that
prove it.

## Uncertainties

- **Q:** What happens when the value parses to a non-finite number
  (`anvil inf km m`, `anvil nan km m`) or when a conversion overflows to
  infinity (`anvil 1e308 km mm`)? R1000 mandates `format(value, ".12g")` on
  every printed result, which prints `inf`; R4 covers "a value that is not a
  number", which reads onto `nan` but not onto overflow. — **risk:** LOW — every
  candidate answer is a single branch inside `convert()`; it moves no slice
  boundary, changes no Signatures block, and S1 and S3 do not pin it. —
  **proposed:** refuse both on the R4 path — an error naming the offending
  input, exit 1 — so the tool never prints `inf` or `nan` as a result.
  **Ruling:** **OD-5 / R1002** (evidence **BL-6**) — refuse both, exactly as
  proposed. The default this plan proceeded on is now a landed requirement, so
  the slice-2 message table stands unchanged; what the ruling adds is the
  measurement, its two rows in `acceptance/S3.sh` and the unit tests beside
  them. Exact message wording stays with this plan, as R4 and R1002 both say.

This plan raises no further uncertainty: OD-5 answers the only one it had, and
nothing in this amendment reaches past what that decision names.

### Derived, not guessed

These were open in `docs/DESIGN.md` and the design layer has since answered
them. They are recorded here as derivations, with what answered them:

- Output precision — **OD-1 / R1000**, `format(value, ".12g")`.
- Positional order, `--batch`, bare `anvil` — **OD-4 / R1001**.
- Non-finite inputs and overflowing results — **OD-5 / R1002**, refused on the
  R4 path.
- `--help` and any other unrecognised flag → usage, standard error, non-zero —
  **R1001**, "every other invocation".
- Which exit code, given "non-zero" — delegated by **R4** and **R5**.
- Module layout, names and signatures — delegated by **§7** and by the Planning
  rule, which makes the Signatures block the plan's job.
- What counts as a number — **§6**: "integer and decimal inputs both occur;
  scientific notation may be ignored". `float()` accepts a superset; §6 permits
  it but does not require it.
- Exact symbol matching — **§5** lists the symbols and **R4** makes anything
  else an unknown unit.
- `-0.0` prints as `-0` — **R1000** names the exact expression, so this is what
  it says.

## The slices

Slices 1 and 2 both touch `src/grimsverk_anvil/cli.py` and
`src/grimsverk_anvil/convert.py`, and slices 1 and 3 both touch
`src/grimsverk_anvil/units.py`. **Assemble in order — 1, then 2 and 3 in
parallel.** Slice 1 creates all three modules; slices 2 and 3 only add to them,
and to disjoint parts. `docs/architecture.md` is appended to by every slice, as
`AGENTS.md` requires; assembly reconciles it.

**The conversion table is fixed here, and both the coder and the test author
work from it.** Base unit metre for length, gram for mass (§8). Multiply by the
factor to reach the base unit.

| Unit | Category | To base | Unit | Category | To base |
| --- | --- | --- | --- | --- | --- |
| `m` | length | `1.0` | `g` | mass | `1.0` |
| `km` | length | `1000.0` | `kg` | mass | `1000.0` |
| `cm` | length | `0.01` | `mg` | mass | `0.001` |
| `mm` | length | `0.001` | `lb` | mass | `453.59237` |
| `mi` | length | `1609.344` | `oz` | mass | `28.349523125` |
| `ft` | length | `0.3048` | | | |
| `in` | length | `0.0254` | | | |

Every factor is the exact international definition: 1 in = 0.0254 m, 1 ft = 12
in, 1 mi = 1760 yd = 1609.344 m, 1 lb = 453.59237 g, 1 oz = 1 lb / 16 =
28.349523125 g. They are exact, not rounded, and V1 makes that non-negotiable.

Conversion is the base-unit hub of §8: `value * from.to_base / to.to_base`,
with both units in the same category.

## Slice 1 — `anvil` converts a length and prints it

- **Delivers:** the installed command works end to end. `anvil 0.1 km m` prints
  `100` and exits 0 — the ESC-1 case, now correct. `anvil 1 mi km` prints
  `1.609344`. `anvil 5000 m km` prints `5`. Anything the converter refuses
  prints `anvil: <reason>` on standard error and exits 1 rather than showing a
  traceback; slice 2 makes those reasons specific and tests them.
- **Files:** `pyproject.toml`, `src/grimsverk_anvil/units.py`, `src/grimsverk_anvil/convert.py`, `src/grimsverk_anvil/cli.py`, `tests/test_convert.py`, `tests/test_format_result.py`, `docs/architecture.md`
- **Estimate:** ~230 lines

**Scope of this slice:** length units only (the seven in the table above);
`pyproject.toml` gains `[project.scripts]` with `anvil =
"grimsverk_anvil.cli:main"`; `cli.py` accepts exactly the three-positional shape
and prints `format_result(...)` plus a newline to standard output.

**`format_result` is R1000 and nothing else.** It is `format(value, ".12g")`.
`tests/test_format_result.py` pins it. These strings were derived by hand from
the rule — Python could not be executed in the planning environment — so **the
rule is the contract and the samples are derived from it**: if a sample and
`format(value, ".12g")` disagree, the format call is right and the disagreement
is a finding for assembly, not something to fix by weakening the rule.

| Input value | Expected string | Why this case |
| --- | --- | --- |
| `100.00000000000001` | `100` | the ESC-1 artifact itself |
| `100.0` | `100` | no trailing zeros, no `.0` |
| `0.5` | `0.5` | ordinary decimal |
| `1 / 3` | `0.333333333333` | 12 significant digits, rounding down |
| `2 / 3` | `0.666666666667` | 12 significant digits, rounding up |
| `28.349523125` | `28.349523125` | 11 digits survive untouched |
| `1e13` | `1e+13` | `g` switches to exponent form at 12 digits |
| `0.00001` | `1e-05` | and below `1e-4` |
| `-0.0` | `-0` | R1000 names the expression; this is what it gives |

`tests/test_convert.py` covers the hub arithmetic on length units in both
directions, including `convert(0.1, "km", "m")` being a value that
`format_result` renders as `100`, and `convert(1.0, "ft", "in")` rendering as
`12`.

### Signatures

```python
@dataclass(frozen=True)
class Unit:
    symbol: str
    category: str  # "length" or "mass"
    to_base: float  # multiply by this to reach the category's base unit


UNITS: dict[str, Unit]


def lookup(symbol: str) -> Unit | None: ...


class ConversionError(Exception):
    """A request that cannot be converted; str(exc) is the user-facing reason."""


def convert(value: float, from_unit: str, to_unit: str) -> float: ...
def format_result(value: float) -> str: ...
def main(argv: Sequence[str] | None = None) -> int: ...
```

`lookup` and `UNITS` live in `units.py`; `ConversionError`, `convert` and
`format_result` in `convert.py`; `main` in `cli.py`. `main` returns the exit
code — the console-script wrapper passes it to `sys.exit` — and reads
`sys.argv[1:]` when `argv` is `None`.

## Slice 2 — `anvil` refuses bad input loudly, and S3 proves it

- **Delivers:** every refusal R4, R5 and R1002 name, with a message that says
  which input was wrong, on standard error, with a non-zero exit — and
  `acceptance/S3.sh` executing them against the installed command.
- **Files:** `src/grimsverk_anvil/convert.py`, `src/grimsverk_anvil/cli.py`, `acceptance/S3.sh`, `tests/test_cli_errors.py`, `docs/architecture.md`
- **Estimate:** ~215 lines (was ~200; the two R1002 rows in `acceptance/S3.sh`
  and their unit tests are what the ruling added — the refusal code itself was
  always in this slice)

The refusals, message shape, and exit code — the message is the contract both
the coder and the test author work from:

| Invocation | Standard error | Exit |
| --- | --- | --- |
| `anvil 5 xyz m` | `anvil: unknown unit: 'xyz'` | 1 |
| `anvil 5 kg m` | `anvil: cannot convert 'kg' (mass) to 'm' (length)` | 1 |
| `anvil abc km m` | `anvil: not a number: 'abc'` | 1 |
| `anvil inf km m` | `anvil: not a number: 'inf'` | 1 |
| `anvil 1e308 km mm` | `anvil: result is out of range: '1e308' km to mm` | 1 |
| `anvil` | the usage text | 2 |
| `anvil 5 km` | the usage text | 2 |
| `anvil 5 km mi extra` | the usage text | 2 |
| `anvil --batch` | the usage text | 2 |
| `anvil --help` | the usage text | 2 |

The last five are R5 and R1001. The usage text is one line:
`usage: anvil <value> <from-unit> <to-unit>`. It does **not** advertise
`--batch`: OD-4 makes `--batch` an unrecognised argument until the
`convert-batch` milestone lands, and usage that names an unimplemented flag is
the silent guess V2 rejects.

The two non-finite rows are **R1002** (OD-5). Refusal happens in `convert.py`:
a value that is not finite after parsing, and a result that is not finite when
the inputs were, both raise `ConversionError`. `tests/test_cli_errors.py` pins
**both branches separately** — the input case (`inf`, `-inf`, `nan`, in any
spelling `float()` accepts) and the overflow case (finite inputs, non-finite
result) — because they are two code paths and one passing test would hide the
other. That is R1002's measurement item (b).

`acceptance/S3.sh` runs the unknown-unit, cross-category, non-numeric, missing,
surplus, **bare `anvil`** and **both non-finite** rows through the installed
command, asserting a non-zero exit and that the message names the offending
input. The bare row is the measurement OD-4 names; `anvil inf km m` and
`anvil 1e308 km mm` are R1002's measurement item (a), and the script must
assert that neither prints `inf` or `nan` on standard output. It prints each
command and what it observed — standard output is the evidence cell — and follows `acceptance/README.md`:
`set -euo pipefail`, exit 0 is pass, offline, no mocks.

### Signatures

```python
def usage() -> str: ...
```

`usage` lives in `cli.py` and returns the single usage line without a trailing
newline. No other signature changes: slice 1 fixed them, and this slice fills in
behaviour behind them.

## Slice 3 — mass units, and S1 as executable evidence

- **Delivers:** `anvil 2 lb oz` prints `32`, `anvil 500 g kg` prints `0.5`, and
  `acceptance/S1.sh` runs a fixed table of 14 known conversions through the
  installed command with exact-match expected strings — including the ESC-1 row.
- **Files:** `src/grimsverk_anvil/units.py`, `acceptance/S1.sh`, `tests/test_convert_mass.py`, `README.md`, `docs/architecture.md`
- **Estimate:** ~150 lines

This slice adds the five mass rows to `UNITS` and nothing else in `src/`: the
hub, the formatter and the CLI already handle any category.

`acceptance/S1.sh` is OD-1's measurement item (b). Its table — the expected
column is exact-match, and every value is a terminating decimal of at most 12
significant digits, so a reader can check the column against the definitions
above without running anything:

| Command | Expected standard output |
| --- | --- |
| `anvil 0.1 km m` | `100` |
| `anvil 1 mi km` | `1.609344` |
| `anvil 1 ft in` | `12` |
| `anvil 100 cm m` | `1` |
| `anvil 2500 mm m` | `2.5` |
| `anvil 3 m cm` | `300` |
| `anvil 1 in cm` | `2.54` |
| `anvil 5000 m km` | `5` |
| `anvil 1 lb kg` | `0.45359237` |
| `anvil 2 lb oz` | `32` |
| `anvil 16 oz lb` | `1` |
| `anvil 500 g kg` | `0.5` |
| `anvil 1 oz g` | `28.349523125` |
| `anvil 2500 mg g` | `2.5` |

Fourteen rows against S1's "at least 10", eight length and six mass, so R1 and
R2 are both exercised. The first row is the ESC-1 case OD-1 requires. The script
prints every row and its result, fails on the first mismatch naming both
strings, and exits 0 only when all fourteen match.

`README.md` gains a short usage section: the two ways to run it, one worked
example, and what the exit codes mean. User-facing behaviour lives in the
README, per `AGENTS.md`.

### Signatures

No new signatures. The mass rows are data in the existing `UNITS` table, and
`tests/test_convert_mass.py` works through `convert` and `format_result` as
declared in slice 1.

## Out of scope

- **Temperature (R3) and batch mode (R6)** — the `temperature` and
  `convert-batch` milestones. The batch line format is still undecided and OD-4
  says the `convert-batch` plan must file it as its own `BL-<n>`.
- **The ESC-1 correction row.** OD-1 item (c) — appending the completing row to
  `docs/escapes.md` citing `acceptance/S1.sh`, and the matching
  `docs/escapes.done.md` closure. `AGENTS.md` forbids a change carrying its own
  ledger entry, so this is a separate one-line `docs/` pull request **after**
  this work merges. It is the last step of OD-1 and it is not optional.
- **`docs/acceptance.md`** — filled by the acceptance pass, not by this plan.
- **BL-1 (aliases), BL-2 (absolute zero), BL-3 (`rich`, halted at OD-2),
  BL-4 (currency, rejected at OD-3).** None of them is planned here, and OD-2
  says not even a stdlib approximation of BL-3.
- **A `--help` flag, a `--version` flag, locale-aware formatting, config
  files.** R1001 and §3.
