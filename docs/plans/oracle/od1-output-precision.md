---
slug: od1-output-precision  # MUST appear in every branch name working this plan
status: draft               # draft | in-flight | merged
created: 2026-08-20
design: MVP milestone `convert` — its print layer (OD-1 places R1000 there)
covers: [R1000]
---

# Output precision (OD-1 / R1000) — Plan

## Summary

**What this builds.** `OD-1` in `docs/DESIGN.oracle.md` added **R1000**: a
printed result value is formatted with `format(value, ".12g")` — at most 12
significant digits, trailing zeros stripped. This plan is one function, one call
site, one acceptance row, and the ledger closure. It resolves `ESC-1`, the
hand-observed `100.00000000000001` printed for 0.1 km in metres.

**Decisions worth saying no to.**

- **Sequencing: this plan is built *after* the `convert` milestone's work has
  merged.** `OD-1` puts R1000 in that milestone's print layer, and the
  measurement `OD-1` names is a row in `acceptance/S1.sh` — a script that cannot
  exist before `anvil` converts anything, because `acceptance-criteria.sh` runs
  every landed criterion script as a required check on **every** pull request.
  An `S1.sh` landed ahead of the conversions it measures is red on every pull
  request until they ship, which stops the build that would make it green.
- **One formatting point.** A new module `src/grimsverk_anvil/output.py` holds
  `format_result(value: float) -> str`, and the CLI prints through it. The later
  `convert-batch` milestone (R6) then inherits R1000 by calling the same
  function instead of re-deciding it.
- **`.12g` semantics are taken literally**, edges included: scientific notation
  at extreme magnitudes (`1e-06` for 1 mg in kg), and `-0` for negative zero.
  `OD-1` named the format function; this plan does not soften it.
- **`ESC-1`'s correction row is its own pull request** (slice 3), after the
  check exists and has been seen red then green. `AGENTS.md` forbids a change
  carrying its own revision of an append-only ledger.

**Deliberately not done.** No change to error or usage text — `OD-1` says those
are prose, not results. No batch wiring: R6 is unbuilt. No rounding inside the
converter and no `decimal` arithmetic — the rule applies at the print point
only. No rows in `docs/acceptance.md`; those belong to the acceptance pass.

**What it costs you.** No dependency, no gate change, nothing new to run. One
extra pull request for the ledger closure.

**Open questions.** One, LOW, filed as `BL-5` and proceeded on: R1000 says
"single-shot and batch output alike", but batch does not exist yet, so this plan
claims `covers: [R1000]` while delivering the single-shot half. If R1000 should
instead be split, that costs one decision and one line of frontmatter here.

## Uncertainties

- **Q:** R1000 requires the rule "in single-shot and batch output alike", but
  batch mode is the unbuilt `convert-batch` milestone (R6) and a steward may not
  widen a plan into it. Does this plan still claim `covers: [R1000]`? —
  **risk:** LOW — every candidate answer leaves the same code, the same slice
  boundaries, the same signature and the same printed output; only the coverage
  bookkeeping differs, and reversing it costs one frontmatter line —
  **proposed:** yes. This plan covers R1000, delivers the single-shot half, and
  makes `format_result` the only place a result becomes text, so the batch plan
  inherits the rule as a one-line call.
  **Ruling:** filed as `BL-5` in `docs/BACKLOG.md`; proceeded on the default
  (LOW), left for the oracle's next cycle.

### Derivations, recorded here rather than filed

These were answered by the design layer and are not uncertainties.

- **Build order.** `OD-1` places R1000 in the MVP `convert` milestone's print
  layer and names `acceptance/S1.sh` as its measurement; `acceptance-criteria.sh`
  makes a landed criterion script a required check on every pull request. Both
  together fix the order: conversions first, this plan second.
- **Where the rule lives.** `OD-1` describes "one format specification applied
  at the single point where a result is printed", and `docs/DESIGN.md` §7 gives
  the CLI layer the printing. The module name, the function name and its
  signature are the plan's to choose, and are chosen below.
- **Non-finite values and negative zero.** R1000 specifies `format(value,
  ".12g")` semantics, which already define `inf`, `nan` and `-0`. Nothing is
  guessed; the tests pin what the format function does.
- **A separate pull request for the ledger row.** `AGENTS.md`: an append-only
  ledger is revised on its own pull request, before or after the work it
  governs, never alongside it.

## The slices

## Slice 1 — `anvil` prints 0.1 km in metres as `100`

- **Delivers:** single-shot results print through the R1000 rule. The `ESC-1`
  case prints exactly `100`, and no conversion prints float noise.
- **Files:** `src/grimsverk_anvil/output.py`, `src/grimsverk_anvil/cli.py`, `tests/test_output.py`, `tests/test_cli_precision.py`
- **Estimate:** ~70 lines

`cli.py` here means the module holding the `anvil` console entry point (R7,
`docs/DESIGN.md` §7). The `convert` milestone builds it first and may name it
otherwise; the change is one import and one call at the point where a converted
value becomes text, and nothing else in this plan depends on the name.

### Signatures

```python
def format_result(value: float) -> str: ...
```

The contract, and it is the whole slice:

- `format_result(value)` returns `format(value, ".12g")`. **That expression is
  the contract.** Where a string listed below disagrees with it, the string is
  wrong.
- Expected strings, for the test author: `100.00000000000001` → `"100"`;
  `0.1 + 0.2` → `"0.3"`; `1 / 3` → `"0.333333333333"`; `1e-06` → `"1e-06"`;
  `1e20` → `"1e+20"`; `0.0` → `"0"`; `-0.0` → `"-0"`; `-2.5` → `"-2.5"`.
- The CLI calls it for the result value and for nothing else. Error text and
  usage text are untouched — `OD-1` rules them prose, not results.
- `tests/test_cli_precision.py` runs the command end to end on the `ESC-1` case
  and asserts the printed value field is exactly `100`.

## Slice 2 — the gate observes the rule on every pull request

- **Delivers:** `acceptance/S1.sh`'s fixed table carries the `ESC-1` case, so
  every later pull request re-checks that 0.1 km in metres prints exactly `100`.
  This is the check `ESC-1` has been waiting for.
- **Files:** `acceptance/S1.sh`, `docs/architecture.md`
- **Estimate:** ~20 lines

### Signatures

No new types or functions. `acceptance/S1.sh` is a shell script and its contract
is the one in `acceptance/README.md`: exit 0 is pass, standard output is the
evidence. The `convert` milestone creates the script; this slice adds one row to
its table, asserting the exact printed string in whatever line format that
milestone settled on. If the table already holds an equivalent 0.1 km row, this
slice tightens it to the exact string rather than adding a second row.

`docs/architecture.md` gains the print layer: one component, responsible for
turning a result value into text, on the single-shot path.

## Slice 3 — `ESC-1` is closed, naming a demonstrated check

- **Delivers:** the escapes ledger stops pointing at an open precision escape,
  and the correction row names a check that exists and was observed working.
- **Files:** `docs/escapes.md`, `docs/escapes.done.md`
- **Estimate:** ~10 lines

Its own pull request, after slices 1 and 2 have merged. Demonstrate the check
before writing the row: run `acceptance/S1.sh` with slice 1's `format_result`
call reverted (red) and restored (green), and record both observations. A row
claiming an undemonstrated check is what `AGENTS.md` refuses.

### Signatures

No code. Two appended rows, both keeping the id `ESC-1`: the correction row in
`docs/escapes.md` naming the demonstrated check, and the closure row in
`docs/escapes.done.md`, which `docs/escapes.md` requires so the oracle is not
handed a finished escape again.

## Out of scope

- Batch mode output (R6, milestone `convert-batch`). It inherits R1000 by
  calling `format_result`; building it here would widen this plan past `OD-1`.
- Converter arithmetic, the unit table, error text and usage text.
- The command-line argument syntax and the batch line format. `docs/DESIGN.md`
  §11 leaves both open and `OD-1` deliberately did not rule on them.
- `docs/acceptance.md` rows — written by the acceptance pass, owner-reviewed.
- `BL-1` and `BL-2` (aliases, absolute zero): no decision has ruled on them.
  `BL-3` is halted by `OD-2` and `BL-4` rejected by `OD-3`; neither is planned.
