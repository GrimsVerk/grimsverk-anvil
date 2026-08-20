---
slug: od8-nonfinite-values  # MUST appear in every branch name working this plan
status: draft               # draft | in-flight | merged
created: 2026-08-20
design: MVP milestone `convert` — its refusal path and its S3 acceptance script (OD-8 places R1003 there)
covers: [R1003]
---

# Non-finite values are refused (OD-8 / R1003) — Plan

## Summary

**What this builds.** `OD-8` added **R1003**: a value token whose parse is not a
finite float — `nan`, `inf`, `-inf`, overflowing literals such as `1e400` — is
"a value that is not a number" under R4, refused with the same named error, the
same streams, the same non-zero exit. The guard is already contracted in
`docs/plans/oracle/od5-convert-cli.md` slice 1, so **no code is commissioned
here**: R1003 adds the §13 observation that plan lacks — two rows in
`acceptance/S3.sh`, run on every future pull request, seen red with the guard
reverted and green with it restored before they are committed.

**Decisions worth saying no to.**

- **Built *after* `od5-convert-cli` merges.** `acceptance/S3.sh` does not exist
  until that milestone writes it, and `acceptance-criteria.sh` runs every landed
  criterion script on every pull request, so this cannot go earlier.
- **One slice, ~25 lines.** Two table rows and one line of architecture doc;
  more slices would be fake, and two cannot share `acceptance/S3.sh` anyway.
- **The rows assert the offending *token*, not the wording.** `od5-convert-cli`
  owns the words (`not a number: '<x>'`); `OD-8` asks only that standard error
  names the token, and pinning the wording would make a later rewording a red
  §13 gate measuring nothing R1003 asked for.
- **Exactly the two rows `OD-8` names**, `nan` and `1e400` — not a sweep of
  every spelling `float()` accepts. R1003 is a finiteness condition precisely so
  the script need not chase that open set.
- **If the guard is missing when this builds, this slice restores it** — rows
  asserting behaviour nothing implements are a gate wired to nothing. Expected
  path: present, and no `src/` or `tests/` file is touched.

**Deliberately not done.** Overflow *during conversion* — a finite input whose
result is infinite, e.g. `1e305` km in mm — which `OD-8` does not cover and no
evidence logs; the run-4 handoff put that to the owner. Whether `1e5` is
accepted at all: §6 leaves it open, `OD-8` does not close it. No
`docs/acceptance.md` rows; no `BL-9` closure line, already retired by citation.

**What it costs you.** No dependency, no gate change, nothing to run by hand.
`acceptance/S3.sh` goes from seven cases to nine, and will turn a pull request
red if `anvil` ever starts answering `nan` — `OD-8`'s named measurement.

**Open questions.** None: every decision was derived from the design layer.
`OD-8` names the two rows and their assertions verbatim and fixes the
sequencing; the derivations below are what make that empty list auditable.

## Uncertainties

No uncertainties — every decision derived from the design.

### Derivations, recorded here rather than filed

Each names what answered it.

- **The two rows and what they assert.** `OD-8`'s Measurement section:
  `anvil nan km mi` with standard error naming `nan`, and `anvil 1e400 km mi`
  with standard error naming `1e400`, "each with a non-zero exit and empty
  standard output, the same assertions the script's existing cases make".
- **That no code is commissioned.** `OD-8` Downstream: "the `convert` plan
  proceeds exactly as landed — the guard is already in its slice 1 contract and
  no slice changes." The run-4 handoff confirms `od5-convert-cli` is untouched.
- **Build order.** `OD-8`: R1003 is "buildable only once the `convert` milestone
  has produced `acceptance/S3.sh`", in "the same after-the-MVP position
  `od1-output-precision` occupies". `acceptance-criteria.sh` runs every landed
  script on every pull request, so a script cannot land ahead of what it measures.
- **Editing a file another plan owns.** Allowed because the two never build at
  once: `AGENTS.md` permits one pipeline pull request in flight per base branch,
  and `od1-output-precision` slice 2 adds a row to `acceptance/S1.sh` the same way.
- **The `1e400` row holds either way on scientific notation.** `OD-8` states it:
  if the parser accepts scientific notation, `1e400` overflows and is refused by
  the finiteness guard; if it rejects it wholesale, `1e400` is already a parse
  error. Both paths name the token.
- **The script's shape.** `acceptance/README.md` — exit 0 is pass, standard
  output is the evidence, `set -euo pipefail`, offline, no mocks — and the
  invocation form the file's existing seven cases already use.
- **The architecture doc line.** `AGENTS.md`: `docs/architecture.md` is updated
  at the end of every slice to describe what now exists, at the level of logic.

## The slices

## Slice 1 — `anvil nan km mi` and `anvil 1e400 km mi` are refused, on every pull request

- **Delivers:** `acceptance/S3.sh` covers nine failure cases instead of seven.
  Running it prints each invocation with what it produced and exits 0; reverting
  the finiteness guard in `parse_value` makes it exit non-zero and say which case
  stopped refusing. `docs/architecture.md` says the value parser accepts only
  finite numbers.
- **Files:** `acceptance/S3.sh`, `docs/architecture.md`
- **Estimate:** ~25 lines

### Signatures

No Python, so no type or function signatures. The script's contract is the one
in `acceptance/README.md`, and this slice does not change it — it appends to the
table `od5-convert-cli` slice 4 established, using that file's existing
invocation form and its existing assertion helper rather than a second style.

Two rows, appended after the seven existing cases:

| invocation | what is asserted on standard error |
| --- | --- |
| `anvil nan km mi` | names `nan` |
| `anvil 1e400 km mi` | names `1e400` |

The contract, for whoever builds it:

- Each new row asserts all three things the existing rows assert: the exit
  status is non-zero, standard error contains the offending token as a
  substring, and standard output is empty.
- "Names the token" is substring containment of `nan` and of `1e400`
  respectively — not equality against `not a number: '<x>'`. The wording is
  `od5-convert-cli`'s to choose and to change; `OD-8` asks only that the token
  appears.
- **Preconditions, checked before writing anything.** `acceptance/S3.sh` exists
  with its seven cases, and `parse_value` raises `NotANumberError` on a
  non-finite parse. If the guard is absent, add it in
  `src/grimsverk_anvil/convert.py` with its unit test in
  `tests/test_convert.py`, worded exactly as `od5-convert-cli` slice 1 contracts
  it, and say in the commit message that a landed plan's contract was missing.
  Those two paths are not in the file list above because the expected path does
  not touch them.
- **Demonstration, before the commit.** Revert the finiteness guard, run
  `acceptance/S3.sh`, and record that it fails on the `nan` case; restore the
  guard, run it again, and record that it passes. `AGENTS.md`'s ratchet takes a
  check that has been seen red against the defect and green against the fix,
  never an undemonstrated one.
- `docs/architecture.md` gains one sentence on the refusal path already
  described there: the value parser yields only finite numbers, so `nan`, the
  infinities, and literals that overflow to infinity are refused exactly like
  any other non-numeric token. Logic, not code — no function names.

## Out of scope

- **Overflow during conversion.** A finite input whose *result* is infinite
  (around `1e305` km in mm) is not R1003, which is a condition on the parse.
  `OD-8` does not decide it and no logged evidence names it; the run-4 handoff
  put it to the owner as a possible backlog line. Nothing here anticipates it.
- **Whether scientific notation is accepted at all.** `docs/DESIGN.md` §6 says
  it "may be ignored" and `OD-8` deliberately leaves it open. R1003 holds on
  either answer, and this plan does not narrow it.
- **The finiteness guard as new work**, and any new unit tests for it. Both
  belong to `docs/plans/oracle/od5-convert-cli.md` slice 1, which `OD-8`
  confirms is untouched. The precondition above is a check, not a slice.
- **Further non-finite spellings** — `-inf`, `Infinity`, `NaN` — beyond the two
  rows `OD-8` names. R1003 covers them by the finiteness condition; the §13
  script samples it, and `od5-convert-cli`'s unit tests carry the breadth.
- **`acceptance/S1.sh`, `format_result`, and the `ESC-1` closure** —
  `docs/plans/oracle/od1-output-precision.md`'s, untouched here.
- **Batch mode (R6).** R1003 is phrased through R4, so batch error lines inherit
  it with no obligation beyond the ones `OD-4` and `OD-5` already recorded for
  the `convert-batch` plan.
- **`docs/acceptance.md`** — written by the acceptance pass and owner-reviewed.
  Nothing here claims a criterion passed.
- **`BL-1` (aliases) and `BL-2` (below absolute zero)** — unruled, so
  unplannable. `BL-3` is halted by `OD-2`, `BL-4` rejected by `OD-3`.
