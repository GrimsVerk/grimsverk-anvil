---
slug: output-precision-r1000
status: draft
created: 2026-08-20
design: (none — no docs/DESIGN.md §12 milestone; this implements oracle decision OD-1, scoped by OD-4)
covers: [R1000]
---

# Output precision — the 12-significant-digit formatting rule — Plan

## Summary

**What this builds.** One pure function — `format_result(value: float) -> str`,
returning `format(value, ".12g")` — in a new module
`src/grimsverk_anvil/output.py`, with blind unit tests asserting its exact output
strings. It is the single point every printed number passes through once a
command exists. It serves **R1000** (`docs/DESIGN.oracle.md`, **OD-1**), which
resolves the first open question in `docs/DESIGN.md` §11 and metabolises
**ESC-1**: the hand-run prototype that printed `100.00000000000001` for 0.1 km
in metres.

**The scope was fixed by OD-4, not chosen here.** OD-4 split OD-1's measurement
in two: this plan delivers the rule and the unit tests that observe it, and the
S1/S2 acceptance scripts land later with the `convert` and `temperature`
milestone plans that build the command they invoke. So this plan builds **no
`anvil` command, no argument parsing, no converter, no acceptance script**, and
decides nothing about CLI syntax.

**Decisions you could say no to.**

- **One slice, not the usual three to five.** The ruled scope is a single pure
  function; splitting it yields a code slice and a test slice — the horizontal
  shape the Planning rule exists to prevent — or work OD-4 forbids.
- **`.12g` is applied verbatim, with no special cases.** R1000 forbids "any
  other rounding, padding, or locale formatting", so `-0.0` prints `-0`, and
  infinity and NaN print `inf` and `nan`. The tests pin all three, so if you
  dislike one the oracle can supersede it against a failing test rather than
  against nothing.
- **A new `output` module, not a helper hung off the converter.** Neither
  converter nor CLI exists yet; R1000 binds the output *path*, and a named
  chokepoint is the thing later plans point at.
- **The ESC-1 correction row is not appended here.** OD-4 assigns it to the
  `convert` implementer, once `acceptance/S1.sh` has landed and run green. ESC-1
  therefore stays open with a pending check after this merges.

**What it costs you.** Nothing new — no dependency, no gate change, no required
check, no manual step. `acceptance-criteria` goes on reporting S1–S5 as
unscripted, the visibility OD-4 chose over placeholder scripts.

**Open questions:** none. Every choice derives from OD-1, OD-4, or R1000's own
text; the derivations are recorded below.

## Uncertainties

**None: every decision derived from the design.** OD-1 and OD-4 in
`docs/DESIGN.oracle.md`, read with `docs/DESIGN.md`, answer every question this
plan had to settle. Recorded here are the choices that could have been
uncertainties and the text that decided each, so the classification can be
checked rather than taken on trust:

- **The digit count and the format string** — R1000 states it verbatim:
  `format(value, ".12g")`. Not a judgment this plan makes; OD-1 already recorded
  it as the judgment call it is, so it can be superseded cheaply.
- **Whether this plan builds a command-line path, or the S1/S2 acceptance
  scripts** — OD-4 rules that it does not, and that the scripts land with the
  plans that build the command they invoke.
- **Non-finite values and negative zero** — R1000's "no other rounding, padding,
  or locale formatting anywhere on the output path" decides it: special-casing
  them would be exactly that. `.12g` passes them through as `inf`, `-inf`, `nan`
  and `-0`.
- **Where the function lives, and what it is called** — program design, which
  the design layer delegates to the plan; `docs/DESIGN.md` §7 sketches "a thin
  CLI layer that … prints" without naming a module.
- **The parameter type** — `float`. §7's converter yields a numeric result and
  §9's table is factors and functions over numbers; `format` accepts `int`
  through the same path unchanged.

None of these is filed as a `BL-<n>`, because none is a gap in the design layer.
`BL-5`, the one real gap this plan hit, was filed by the previous steward run
and ruled on by OD-4 before this plan was written.

## The slices

## Slice 1 — Every conversion result formats to at most 12 significant digits

- **Delivers:** a caller can format a conversion result and get R1000's exact
  string. Observable end to end from a checkout:
  `python -c "from grimsverk_anvil.output import format_result; print(format_result(0.1 * 1000))"`
  prints `100`, where `python -c "print(0.1 * 1000)"` prints
  `100.00000000000001`. ESC-1's artifact is dead at the only place a result is
  ever turned into text.
- **Files:** `src/grimsverk_anvil/output.py`, `tests/test_output.py`, `docs/architecture.md`
- **Estimate:** ~100 lines

### Signatures

```python
def format_result(value: float) -> str: ...
```

`format_result` returns `format(value, ".12g")` and does nothing else: no
rounding of its own, no padding, no width, no thousands separator, no unit
suffix, no locale awareness (R1000). It is total — every `float` has a result,
including the non-finite ones — and it has no other public names.

### The behaviour contract

This table is the agreement between the two agents building this slice, who
cannot see each other's work. Each row is `format_result(<input>)` and the exact
string it returns.

| Input expression | Exact result | Why this row is here |
| --- | --- | --- |
| `0.1 * 1000` | `100` | the ESC-1 reproduction, named by OD-1 |
| `100 * 9 / 5 + 32` | `212` | S2 fixture, named by OD-1 |
| `100 + 273.15` | `373.15` | S2 fixture, named by OD-1 |
| `1 / 3` | `0.333333333333` | the 12-digit cut itself |
| `2.50` | `2.5` | trailing zeros stripped |
| `-40.0` | `-40` | a negative, and an integral float |
| `0.0` | `0` | zero |
| `-0.0` | `-0` | signed zero passes through, not special-cased |
| `1e-3 / 1e3` | `1e-06` | 1 mm in km — small magnitudes stay exact, not `0.00` |
| `1e-05` | `1e-05` | scientific below the `g` threshold |
| `0.0001` | `0.0001` | fixed notation at the threshold |
| `1e11` | `100000000000` | fixed notation below 12 digits of exponent |
| `1e12` | `1e+12` | scientific at and above it |
| `float("inf")` | `inf` | non-finite passes through |
| `float("-inf")` | `-inf` | non-finite passes through |
| `float("nan")` | `nan` | non-finite passes through |

Three constraints on how these are tested, and they are the point of the slice
rather than detail:

1. **Compare exact strings, never parsed floats.** OD-1 says why: a numeric
   comparison accepts the artifact ESC-1 logged.
2. **Build the ESC-1 input by arithmetic**, as `0.1 * 1000`, not by pasting the
   literal `100.00000000000001`. A pasted literal restates the artifact; the
   arithmetic reproduces it, which is what makes the test red against the defect
   — the naive implementation, `str(value)`, returns `100.00000000000001` and
   fails this row — and green against the fix.
3. **No test may assert `format(value, ".12g")` on both sides.** An assertion
   that recomputes the rule it is checking passes against any implementation of
   it, including a wrong one.

**On the rows OD-1 does not name.** The three rows OD-1 states — `100`, `212`,
`373.15` — are normative. The rest are this plan's reading of CPython's `g`
conversion (scientific notation when the decimal exponent is below -4 or at
least the precision, 12; trailing zeros stripped), derived rather than observed:
the session that wrote this plan could not execute Python. R1000 defines the
output as `format(value, ".12g")`, so if a derived row and CPython disagree, the
row is wrong and the implementation is right — correct the row and say so in the
commit, per the `Blind-Tests` rule. That licence extends to these rows only; it
is not licence to weaken a row that is failing because the implementation is
wrong, and it never touches the three normative ones.

### Architecture doc

At the end of the slice, `docs/architecture.md` records what now exists: an
`output` component whose single responsibility is turning a numeric result into
the text `anvil` prints, that this is the one place that formatting happens, and
that nothing yet calls it — a converter and a CLI are the next things built, and
they call it rather than formatting numbers themselves. That last sentence is
what makes R1000's "anywhere on the output path" clause legible to whoever
builds the `convert` milestone.

## Out of scope

Everything here is excluded by OD-4, by OD-2, or by `docs/DESIGN.md`, not by
preference:

- **The `anvil` command** — no console entry point, no `pyproject.toml`
  `[project.scripts]`, no argument parsing, no `__main__`. R7 is untouched.
- **The converter and the unit table** — R1, R2, R3 belong to the `convert` and
  `temperature` milestones.
- **`acceptance/S1.sh` and `acceptance/S2.sh`** — OD-4 places them in the
  `convert` and `temperature` plans respectively, in the same plan as the
  command each invokes. No acceptance script lands before its command exists,
  and no placeholder script stands in for one: the `acceptance-criteria` check's
  per-pull-request "no script yet" report is the intended visibility.
- **The ESC-1 correction row in `docs/escapes.md`** — OD-4 assigns it to the
  `convert` implementer after S1 runs green. The unit tests here are necessary
  but are not the check that stub is waiting on.
- **The exact CLI syntax and the batch line format** — `docs/DESIGN.md` §11,
  still open; OD-1 and OD-4 both leave them so, and the `convert` planner files
  them as uncertainties when planning reaches them.
- **Aligned or coloured output, and any table rendering** — declined by OD-2,
  including a hand-rolled standard-library substitute.
- **Any change to `docs/DESIGN.md`, `docs/DESIGN.oracle.md`, `docs/VISION.md`,
  or any gate path.**

## What this decision makes partly wrong

Nothing yet. `docs/plans/` holds only `_TEMPLATE.md` and this plan, so OD-1
invalidates no existing plan — as OD-1 itself records.

Two *future* plans inherit constraints from it, which is the closest thing to an
invalidation here and is worth naming so neither planner rediscovers it:

- **Milestone `convert`** must call `format_result` on its output path rather
  than formatting numbers itself, must deliver `acceptance/S1.sh` comparing the
  installed command's exact stdout strings with the 0.1 km → m row in its fixed
  table, and its implementer appends the ESC-1 correction row once that script
  has run green.
- **Milestone `temperature`** must do the same for `acceptance/S2.sh`, whose
  fixtures print exactly `212` and `373.15`.
