---
slug: anvil-temperature     # MUST appear in every branch name working this plan
status: draft               # draft | in-flight | merged
created: 2026-08-20
design: Later — milestone `temperature` (docs/DESIGN.md §12)
covers: [R3, R7, R8]
---

# `anvil` temperature — Plan

## Summary

**What this builds.** Milestone `temperature`: `anvil` converts between C, F and
K, offsets included, through the same command line and the same output rule the
`convert` MVP established. It delivers the design's **R3**, and carries **R7**
and **R8** — the non-functional platform and dependency requirements no §12
milestone names (see Uncertainties, BL-7).

**This plan builds on the MVP's code, so it is second in the queue.**
`docs/plans/oracle/anvil-convert-mvp.md` creates `units.py`, `convert.py` and
`cli.py`; this plan extends all of them and cannot start before that work has
merged.

**Decisions that are expensive to reverse.**

- **The unit table becomes affine.** `Unit.to_base: float` — one factor — is
  replaced by a pair of callables `to_base` / `from_base`, exactly the record
  §9 names, with §8's "temperatures as functions" as the reason. Length and mass
  rows are built by a `scaled(...)` helper. This edits the MVP's Signatures
  block, which is why it is here and not in a slice comment.
- **The arithmetic of every existing conversion is unchanged.** For a scaled
  unit `to_base(v) = v * factor` and `from_base(v) = v / factor`, so
  `to.from_base(from.to_base(value))` is the same expression, in the same order,
  as the MVP's `value * from.to_base / to.to_base`. **`acceptance/S1.sh`'s
  fourteen expected strings must not change.** If one does, the refactor is
  wrong — do not edit S1.
- **Base unit kelvin**, per §8. C↔F always goes through K; there is no direct
  pair.
- **Symbols are `C`, `F`, `K`, matched exactly** — `c` is an unknown unit, as
  `KM` is. Casing and spelled-out names are BL-1, owner-filed, not commissioned.
- **A third category string, `temperature`**, so R4's cross-category message
  reads `anvil: cannot convert 'C' (temperature) to 'm' (length)`.

**What it costs you.**

- One new required-check script, `acceptance/S2.sh`, running on **every** pull
  request from here on.
- Nothing else: no dependency (V5 holds), no new module, no CLI surface. The
  three-positional shape of R1001 already covers `anvil 350 F C`.

**Deliberately not done.** Batch mode (R6) — the `convert-batch` milestone, and
its line format is still undecided. **Absolute zero is not checked**: today
`anvil -300 C K` prints `-26.85`, a physically impossible temperature. That is
BL-2, owner-filed and not commissioned, and this plan does not pre-empt it.

**Open questions.** One, and it is LOW: which plan carries R7 and R8. Filed as
**BL-7**, proceeded on the default that this plan carries them.

## Uncertainties

- **Q:** Which plan covers **R7** (a Python CLI installed as the console
  command `anvil` from package `grimsverk_anvil`) and **R8** (standard library
  only, offline and deterministic)? `docs/DESIGN.md` §12 names two remaining
  milestones, `temperature` (R3) and `convert-batch` (R6), and neither names
  them; both are evidenced only by **S4**, which §13 marks **(owner)**, so no
  acceptance script can ever cover them and `coverage.sh` reports them
  unplanned until some plan lists them. — **risk:** LOW — the entire question
  is one line of front matter. It moves no slice boundary, changes no
  Signatures block, alters no acceptance script's expected values and no
  external format; reversing it is a one-line `docs/` pull request. —
  **proposed:** this plan lists them alongside R3, because it is the first plan
  whose acceptance script (`acceptance/S2.sh`) exercises the installed `anvil`
  console command end to end, which is R7's whole substance, and because it
  adds no dependency, which is R8's.
  **Ruling:** proceeded on the default (LOW), filed as **BL-7** for the
  oracle's next cycle.

### Derived, not guessed

These looked open and are not — the design layer answers each one, and the
answer is recorded here with what gave it:

- Temperatures as functions rather than factors — **§8**, the decision is
  taken there: *"functions — Fahrenheit/Celsius have offsets, factors silently
  produce wrong answers."*
- The record shape `to_base` / `from_base` on one table — **§9**:
  *"A unit table: `{unit_symbol: (category, to_base, from_base)}`"*.
- Kelvin as the temperature base unit — **§8**, "metre, gram, kelvin".
- Which symbols exist — **§5 R3** names C, F, K; **R4** makes anything else an
  unknown unit.
- Output precision, including what the round trip prints — **OD-1 / R1000**,
  `format(value, ".12g")`.
- The command line for a temperature conversion — **OD-4 / R1001**, three
  positionals; nothing here is a new invocation shape.
- Non-finite results on the temperature path (`anvil 1e308 C F` overflows in
  `from_base`) — **OD-5 / R1002**, refused on the R4 path.
- Module layout, names and signatures — delegated by **§7** and by the
  Planning rule, which makes the Signatures block the plan's job.
- Exit codes 1 and 2 — fixed by the MVP plan, which R4 and R5 delegated to it.

## The slices

Slice 1 changes `src/grimsverk_anvil/units.py` and
`src/grimsverk_anvil/convert.py`; slices 2 and 3 touch neither. **Assemble in
order — 1, then 2 and 3 in parallel.** `docs/architecture.md` is appended to by
every slice, as `AGENTS.md` requires; assembly reconciles it.

**The temperature table is fixed here, and both the coder and the test author
work from it.** Base unit kelvin. Conversion is
`to.from_base(from.to_base(value))`, with both units in the same category.

| Unit | Category | To base (kelvin) | From base (kelvin) |
| --- | --- | --- | --- |
| `K` | temperature | `k` | `k` |
| `C` | temperature | `c + 273.15` | `k - 273.15` |
| `F` | temperature | `(f - 32.0) * 5.0 / 9.0 + 273.15` | `(k - 273.15) * 9.0 / 5.0 + 32.0` |

These are the exact definitions: the Celsius and Kelvin degree are the same
size and offset by exactly 273.15, and one Fahrenheit degree is exactly 5/9 of
one Celsius degree with zero Celsius at 32 Fahrenheit. Write `5.0 / 9.0`, never
a decimal approximation of it — V1 makes that non-negotiable, and `0.5556`
would fail S2's round trip.

**Expected strings were derived by hand from R1000** — Python could not be
executed in the planning environment — so **the rule is the contract and the
samples are derived from it**: if a sample and `format(value, ".12g")`
disagree, the format call is right and the disagreement is a finding for
assembly, not something to fix by weakening the rule or by editing the table
above.

## Slice 1 — the table goes affine, and Celsius, Fahrenheit and Kelvin convert

- **Delivers:** `anvil 100 C F` prints `212`, `anvil 100 C K` prints `373.15`, `anvil 0 K C` prints `-273.15`, `anvil 350 F C` prints `176.666666667` — and every length and mass conversion prints exactly what it printed before, unchanged.
- **Files:** `src/grimsverk_anvil/units.py`, `src/grimsverk_anvil/convert.py`, `tests/test_units_affine.py`, `docs/architecture.md`
- **Estimate:** ~200 lines

**Scope of this slice:** `Unit` gains the `to_base` / `from_base` callable pair
in place of the single factor; `scaled(...)` rebuilds the twelve length and mass
rows from the factors already pinned in the MVP plan's table, unchanged; the
three temperature rows are added; `convert` composes the pair instead of
multiplying and dividing. `cli.py` is not touched — R1001's three positionals
already carry a temperature conversion.

`tests/test_units_affine.py` pins, through `convert` and `format_result`:

| Conversion | Formatted result | Why this case |
| --- | --- | --- |
| `convert(100, "C", "F")` | `212` | §13 S2, the headline case |
| `convert(100, "C", "K")` | `373.15` | §13 S2 |
| `convert(0, "C", "C")` | `0` | same unit, both directions applied |
| `convert(32, "F", "C")` | `0` | the other fixed point |
| `convert(0, "K", "C")` | `-273.15` | absolute zero, and a negative result |
| `convert(-40, "C", "F")` | `-40` | the crossing point — catches a swapped `9/5` |
| `convert(350, "F", "C")` | `176.666666667` | §4's oven case, non-terminating |
| `convert(1, "ft", "in")` | `12` | a scaled unit still works after the refactor |
| `convert(1, "lb", "kg")` | `0.45359237` | and so does a mass unit |

The last two rows are the regression guard the refactor needs: the point of
`scaled(...)` is that the MVP's arithmetic survives it.

### Signatures

```python
Conversion = Callable[[float], float]


@dataclass(frozen=True)
class Unit:
    symbol: str
    category: str  # "length", "mass" or "temperature"
    to_base: Conversion  # this unit -> the category's base unit
    from_base: Conversion  # the category's base unit -> this unit


UNITS: dict[str, Unit]


def scaled(symbol: str, category: str, factor: float) -> Unit: ...
def lookup(symbol: str) -> Unit | None: ...
```

`Conversion`, `Unit`, `scaled`, `UNITS` and `lookup` live in `units.py`.
`scaled` returns a `Unit` whose `to_base` multiplies by `factor` and whose
`from_base` divides by it. The four temperature conversions are module-private
functions in `units.py`; tests reach them through `convert` and `lookup`, never
by name. `convert`, `format_result` and `main` keep the signatures the MVP plan
declared — only `convert`'s body changes.

## Slice 2 — S2 as executable evidence

- **Delivers:** `acceptance/S2.sh`, a required check on every pull request, proving R3 against the installed command: the two fixed values §13 names, and a C→F→K→C round trip run as three real invocations that returns to the start string.
- **Files:** `acceptance/S2.sh`, `tests/test_cli_temperature.py`, `docs/architecture.md`
- **Estimate:** ~180 lines

`acceptance/S2.sh` runs each row through the installed `anvil` command and
compares standard output **exact-match**, which R1000 makes deterministic:

| Command | Expected standard output |
| --- | --- |
| `anvil 100 C F` | `212` |
| `anvil 100 C K` | `373.15` |
| `anvil 32 F C` | `0` |
| `anvil 0 K C` | `-273.15` |
| `anvil -40 C F` | `-40` |
| `anvil 212 F K` | `373.15` |

Then the round trip, as three chained invocations, each fed the previous one's
standard output:

    100 --(anvil 100 C F)--> 212 --(anvil 212 F K)--> 373.15
        --(anvil 373.15 K C)--> 100

and the script asserts the final string is exactly `100`, the string it
started from. Feeding the printed string back in is the point: it proves the
round trip through the tool a user actually has, not through a float a test
kept in memory. It is also why 12 significant digits is load-bearing — the
subtraction at the last step lands a few parts in a quadrillion away from 100,
and R1000 is what makes it print `100`.

The script prints every command and what it observed — standard output is the
evidence cell — and follows `acceptance/README.md`: `set -euo pipefail`, exit 0
is pass, offline, no mocks, fail on the first mismatch naming both strings.

`tests/test_cli_temperature.py` drives `main(...)` for the same rows plus
`anvil 350 F C`, asserting exit code 0 and the exact line on standard output.

### Signatures

No new signatures. This slice exercises `main` as slice 1 and the MVP plan
declared it.

## Slice 3 — temperature refuses like everything else, and the README says so

- **Delivers:** `anvil 5 C m` refuses with a message naming the new category, `anvil 1e308 C F` refuses instead of printing `inf`, `anvil 100 c f` refuses as an unknown unit — and the README documents temperature conversion.
- **Files:** `README.md`, `tests/test_temperature_errors.py`, `docs/architecture.md`
- **Estimate:** ~130 lines

| Invocation | Standard error | Exit |
| --- | --- | --- |
| `anvil 5 C m` | `anvil: cannot convert 'C' (temperature) to 'm' (length)` | 1 |
| `anvil 5 kg K` | `anvil: cannot convert 'kg' (mass) to 'K' (temperature)` | 1 |
| `anvil 100 c f` | `anvil: unknown unit: 'c'` | 1 |
| `anvil 1e308 C F` | `anvil: result is out of range: '1e308' C to F` | 1 |

**No `src/` change is expected in this slice.** The messages are the MVP's,
parameterised by category and symbol, and the overflow branch is R1002's, which
the MVP built; a temperature conversion simply flows through both. If the
implementation turns out to need a change here, the composition assumption was
wrong, and surfacing that is exactly what this slice is for — say so at
assembly rather than quietly widening slice 1.

The overflow row is R1002 on the temperature path: `1e308 + 273.15` is finite,
and `from_base` for Fahrenheit multiplies it by 9/5, which is not. Pin it
separately from the non-finite-input case.

`README.md` gains temperature to its usage section: the three symbols, one
worked example (`anvil 350 F C`), and one line saying the tool does not check
for physically impossible temperatures.

### Signatures

No new signatures.

## Out of scope

- **Batch mode (R6)** — the `convert-batch` milestone. Its line format is still
  undecided, and OD-4 says that plan must file it as its own `BL-<n>`.
- **Absolute zero (BL-2)** — owner-filed, not commissioned, and the oracle's
  handoff says items in Proposed move only when the owner moves them. A
  temperature below absolute zero converts normally today.
- **Unit aliases and casing (BL-1)**, **pretty output (BL-3, halted at OD-2)**,
  **currency (BL-4, rejected at OD-3)**.
- **`acceptance/S1.sh` and `acceptance/S3.sh`** — the MVP plan's scripts, for
  criteria this plan does not cover. Slice 1 must leave S1's expected strings
  byte-identical; adding temperature rows to S3 would be extending another
  plan's criterion.
- **`docs/acceptance.md`** — filled by the acceptance pass, not by this plan.
- **`docs/escapes.md`** — this plan closes no escape, and `AGENTS.md` forbids a
  change carrying its own ledger entry in any case.
