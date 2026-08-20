---
slug: temperature-conversions  # MUST appear in every branch name working this plan
status: draft                  # draft | in-flight | merged
created: 2026-08-20
design: milestone `temperature` (docs/DESIGN.md §12, "Later") — temperature support (R3), S2 passes
covers: [R3]
---

# The `temperature` milestone — C, F and K (R3) — Plan

## Summary

**What this builds.** The `temperature` milestone (`docs/DESIGN.md` §12):
`anvil 100 C F` prints `212`, `anvil 100 C K` prints `373.15`, and a C→F→K→C
round trip through the installed command returns to the start value.
`acceptance/S2.sh` then checks that on every future pull request.
`covers: [R3]`, exactly the requirement §12 gives this milestone.

**Decisions worth saying no to.**

- **Every unit gets a `to_base` and a `from_base` function**, replacing the
  single `to_base` factor `od5-convert-cli` shipped — the table §9 specifies,
  and §8 says temperatures must be functions. A `linear(symbol, category,
  factor)` helper keeps length and mass entries one line each (§8).
- **Length and mass arithmetic is unchanged, expression for expression** —
  `value * source_factor / target_factor`. `acceptance/S1.sh`'s twelve strings
  must stay green bit for bit; if one moves, that is a defect, not a row to fix.
- **Kelvin is the base unit** (§8), so C→F goes C→K→F. The conversions are
  pinned as `value * 9.0 / 5.0`, not `value * 1.8`: the ordering is what makes
  S2's expected strings exact rather than nearly exact.
- **No change to `cli.py`, `output.py`, `pyproject.toml` or the error wording.**
  The CLI is unit-agnostic — it parses, calls `convert`, prints — so temperature
  works the moment the table knows the symbols. Hence two slices, not four.
- **`C`, `F`, `K` matched exactly and case-sensitively**, as R1001 (`OD-5`)
  requires and §5 spells them. `c` and `kelvin` are unknown units today.
- **Nothing rejects an impossible temperature.** `anvil -500 C K` will print
  `-226.85`. That is `BL-2`, still unruled, so it cannot be planned.

**Deliberately not done.** Batch mode (R6) — the next milestone. Absolute zero
(`BL-2`) and aliases (`BL-1`) — unruled. Any change to `acceptance/S1.sh` or
`acceptance/S3.sh`. `docs/acceptance.md` rows — the acceptance pass writes those.

**What it costs you.** No dependency, no gate change, nothing to run by hand.
One new acceptance script, `S2`, then runs on **every** future pull request and
will turn one red if temperature output ever changes.

**Open questions.** None. Every decision came from `docs/DESIGN.md` §5, §8, §9
and §12 or from `OD-5`/`OD-6`; the derivations below make that empty list
auditable.

## Uncertainties

No uncertainties — every decision derived from the design.

### Derivations, recorded here rather than filed

Each names what answered it.

- **The unit table's shape.** `docs/DESIGN.md` §9 gives it verbatim:
  `{unit_symbol: (category, to_base, from_base)}` — a `from_base` per unit, not
  per category — and §8 says "temperatures as functions, since they are affine,
  not linear". `od5-convert-cli` shipped the narrower `to_base: float` because
  it had only linear categories; R3 is what forces §9's full shape. The module,
  the helper name and the dataclass field types are program design the design
  layer delegates, and are fixed in the Signatures block below.
- **Kelvin as the base unit.** §8: "conversions go through a canonical base
  unit per category (metre, gram, kelvin)".
- **The three symbols and their case.** §5 R3 spells them `C`, `F`, `K`; R1001
  (`OD-5`) pins §5's spelling, matched exactly and case-sensitively, "if `BL-1`
  is later granted, its decision supersedes this matching sentence only".
- **The output.** R1000 (`OD-1`) and R1002 (`OD-6`) are unit-agnostic: one line
  on standard output, `format(value, ".12g")` of the result, nothing else. No
  print point is added here, so nothing is re-decided.
- **Cross-category refusal.** R4 already makes `kg` to `m` an error and
  `od5-convert-cli` fixed the message; a third category joins that rule with no
  new machinery. `anvil 100 C m` refuses by the path that already exists.
- **Which criterion this milestone owes.** §12: "Milestone `temperature` —
  temperature support (R3): S2 passes." So `acceptance/S2.sh` is this plan's,
  and S1 and S3 are not.
- **Build order.** This plan builds after `docs/plans/oracle/od5-convert-cli.md`
  has merged: it edits that milestone's `units.py` and `convert.py`, and
  `acceptance/S2.sh` invokes the installed console command R7 creates there.
  `acceptance-criteria.sh` runs every landed criterion script on every pull
  request, so S2 cannot land ahead of what it measures. No ordering against
  `od1-output-precision` or `od8-nonfinite-values`: no file is shared.
- **Editing files another plan owns.** Allowed because the two never build at
  once — `AGENTS.md` permits one pipeline pull request in flight per base
  branch — and it is the same move `od8-nonfinite-values` makes on
  `acceptance/S3.sh`.
- **`BL-2` is not planned.** It sits in `docs/BACKLOG.md`'s **Proposed**
  section, which is "ideas, written as text, never coded unprompted", and the
  run-4 oracle handoff repeats it: "Still unruled; no decision cites them, so
  nothing may plan them." R3 as written asks for the offset math and nothing
  about domain validation, so building it unguarded implements the design
  rather than guessing past it.

## The slices

Two slices, and a third would be fake: the CLI needs no change, so the only work
is the table plus the criterion script, and those two cannot share a file
anyway. Slice workers build in parallel worktrees off the same base
(`.claude/orchestration.md`), so no file is named twice below.

## Slice 1 — `anvil 100 C F` prints `212`

- **Delivers:** temperature conversion end to end through the installed
  command. `anvil 100 C F` prints `212`, `anvil 100 C K` prints `373.15`,
  `anvil 212 F C` prints `100`, `anvil -40 C F` prints `-40`, and
  `anvil 100 C m` still refuses by naming both units. Length and mass output is
  unchanged.
- **Files:** `src/grimsverk_anvil/units.py`, `src/grimsverk_anvil/convert.py`, `tests/test_units.py`, `tests/test_convert.py`
- **Estimate:** ~135 lines

### Signatures

```python
Category = Literal["length", "mass", "temperature"]
Scale = Callable[[float], float]


@dataclass(frozen=True)
class Unit:
    symbol: str
    category: Category
    to_base: Scale
    from_base: Scale


UNITS: dict[str, Unit]


def linear(symbol: str, category: Category, factor: float) -> Unit: ...
def celsius_to_kelvin(value: float) -> float: ...
def kelvin_to_celsius(value: float) -> float: ...
def fahrenheit_to_kelvin(value: float) -> float: ...
def kelvin_to_fahrenheit(value: float) -> float: ...
def convert(value: float, from_symbol: str, to_symbol: str) -> float: ...
```

The contract, for the test author and the coder alike:

- `Unit.to_base` and `Unit.from_base` are functions on every unit, per §9.
  `linear(symbol, category, factor)` returns a `Unit` whose `to_base` is
  `value * factor` and whose `from_base` is `value / factor`, so the twelve
  length and mass entries stay one line each and keep the factors
  `od5-convert-cli` fixed (`km` 1000, `cm` 0.01, `mm` 0.001, `mi` 1609.344,
  `ft` 0.3048, `in` 0.0254, `m` 1; `kg` 1000, `g` 1, `mg` 0.001, `lb`
  453.59237, `oz` 28.349523125).
- `convert` returns `target.from_base(source.to_base(value))`. For a linear
  pair that expands to `value * source_factor / target_factor` — **the same
  expression, in the same order, as before this slice** — so every existing
  `acceptance/S1.sh` string is unchanged. `UnknownUnitError` (source symbol
  checked first), `CategoryMismatchError`, and same-unit conversion all behave
  exactly as `od5-convert-cli` slice 1 contracts them.
- Three new entries, category `temperature`, base kelvin, keyed exactly `C`,
  `F`, `K`. Fifteen entries in `UNITS`, no more.
- The four conversion functions, pinned literally, because the ordering decides
  whether S2's strings are exact:
  - `celsius_to_kelvin(value)` → `value + 273.15`
  - `kelvin_to_celsius(value)` → `value - 273.15`
  - `fahrenheit_to_kelvin(value)` → `(value - 32.0) * 5.0 / 9.0 + 273.15`
  - `kelvin_to_fahrenheit(value)` → `(value - 273.15) * 9.0 / 5.0 + 32.0`
  `K` uses the identity for both directions.
- Worked results, as the printed line `format(value, ".12g")` produces them:
  `100 C F` → `212`; `100 C K` → `373.15`; `212 F K` → `373.15`;
  `373.15 K C` → `100`; `0 C F` → `32`; `0 C K` → `273.15`;
  `-40 C F` → `-40`; `-273.15 C K` → `0`; `100 C C` → `100`.
  Where a string here disagrees with the expression above, **the expression is
  the contract** and the string is wrong — record the observed output in the
  commit message when that happens.
- `anvil 100 C m` and `anvil 5 km C` raise `CategoryMismatchError`, wording
  unchanged, e.g. `cannot convert temperature to length: 'C' and 'm'`.
- `c`, `f`, `k`, `celsius` and `kelvin` are unknown units and raise
  `UnknownUnitError` (R1001).
- Tests cover: the new table shape for a linear unit and a temperature unit;
  each of the four conversion functions directly; the worked results above; the
  round trip 100 C → F → K → C returning `100.0`; both cross-category pairs;
  the rejected spellings. `tests/test_units.py` and `tests/test_convert.py`
  already exist from `od5-convert-cli` — extend them, and update any assertion
  that reads `to_base` as a number rather than calling it.

## Slice 2 — S2 checks the temperature contract on every pull request

- **Delivers:** `acceptance/S2.sh`, the executable form of §13's S2 (R3). It
  runs the installed command, prints each invocation with what it produced, and
  exits 0 only if every expected line matched. `docs/architecture.md` describes
  the milestone as built.
- **Files:** `acceptance/S2.sh`, `docs/architecture.md`
- **Estimate:** ~65 lines

### Signatures

No Python, so no type or function signatures. The script's contract is the one
in `acceptance/README.md` — exit 0 is pass, standard output is the evidence,
`set -euo pipefail`, offline, no mocks — and it uses the same invocation form
and assertion style `acceptance/S1.sh` established (`uv run --frozen anvil …`,
never `python -m` and never an import, because S2 says "verified through the
installed `anvil` command").

Two parts, both named by S2 itself:

**The fixed pair.** Entire-standard-output-line equality, the comparison `OD-6`
obliges:

    100 C F     212
    100 C K     373.15

**The round trip.** `C→F→K→C`, chaining three invocations so each step consumes
the previous step's printed line, starting from `100`:

    step 1:  anvil 100 C F   -> 212
    step 2:  anvil 212 F K   -> 373.15
    step 3:  anvil 373.15 K C -> 100

The assertion is that step 3's line equals the start value's printed form,
`100`. Chaining printed lines rather than raw floats is what "verified through
the installed `anvil` command" means, and R1002 makes the printed line the only
thing the command exposes.

- Every step also asserts exit status 0 and empty standard error.
- The script prints each command and its output before the verdict, so a
  failure says which step drifted rather than only that S2 failed.
- If a value here disagrees with what slice 1's pinned expressions produce, the
  expressions win and this script is corrected — but note that would mean the
  chain is no longer exact, which is a finding worth a `BL-<n>` rather than a
  silently loosened comparison.

`docs/architecture.md` gains: temperature as a third category on the existing
unit table; that a unit now carries a pair of conversion functions rather than a
factor, with kelvin as the temperature base; and one line saying the CLI path is
unchanged, so a temperature request travels the same route as a length one.
Logic, not code — no function names.

## Out of scope

- **Batch mode (R6)** — milestone `convert-batch`. `--batch` stays the usage
  error R1001 reserves. That milestone's obligations from `OD-4` and `OD-5` are
  not this plan's.
- **Below absolute zero (`BL-2`)** — unruled, so unplannable, and the run-4
  oracle handoff says so explicitly. The consequence is concrete and stated
  here rather than discovered later: once this milestone lands,
  `anvil -500 C K` prints `-226.85` and `anvil -500 C F` prints `-868`. If that
  is wrong, it is `BL-2`'s ruling to make, and it costs one guard in
  `convert` plus rows in an acceptance script.
- **Aliases (`BL-1`)** — unruled. `BL-3` is halted by `OD-2`, `BL-4` rejected
  by `OD-3`; neither is planned.
- **`acceptance/S1.sh` and `acceptance/S3.sh`** — untouched. S1's rows belong
  to `od5-convert-cli` and `od1-output-precision`; S3's to `od5-convert-cli`
  and `od8-nonfinite-values`. No temperature row is added to S3: R4's
  cross-category rule is already observed there, and adding a case for a
  category S3 was not written for would widen this plan past R3.
- **`format_result`, the `ESC-1` closure, and the print layer** —
  `od1-output-precision`'s. Nothing here adds a place where a value becomes
  text.
- **Overflow during conversion** — the run-4 handoff's open observation, with
  no logged evidence and no ruling. A temperature conversion cannot reach it
  from a finite input, and nothing here anticipates it.
- **`docs/acceptance.md`** — written by the acceptance pass and owner-reviewed.
  Nothing here claims a criterion passed.
