# Design decisions from evidence — grimsverk-anvil

The **second design document**, and the only one an agent may write while nobody
is awake.

`docs/DESIGN.md` is `CODEOWNERS`-owned: a change to it waits for the owner. That
is correct — it is the standard every pull request is judged against — and it is
also why unattended work stops at the first thing the evidence contradicts. This
file is the answer. It is append-only, mechanically checked
(`.github/scripts/oracle-decisions.sh`), and deliberately **not** owned, because
ownership here would stop overnight work, which is the point of having it.

Its author is the **oracle** (`/oracle`). Nothing else writes here.

## What may be decided

Only what the evidence already logged. A decision resolves a **recorded
contradiction** between the design and reality:

- an escape — `ESC-<n>` in `docs/escapes.md`;
- a backlog item — `BL-<n>` in `docs/BACKLOG.md`.

Both are cited by rigid id and both must already exist on the default branch.
The oracle cannot invent a design change, and this is what makes that a fact
rather than an instruction: an idea with no logged evidence behind it has
nowhere to be written down. It is not a place to record improvements someone
thought of — those go to `docs/BACKLOG.md` like every other proposal.

**Give backlog items ids** (`BL-1`, `BL-2`, …) if you want them citable. An item
with no id is not evidence as far as the check is concerned.

## Requirement ids start at R1000

Requirement ids share ONE integer space with `docs/DESIGN.md` — the grammar is
`R` followed by digits and there is no namespace mechanism — so anything
numbered here would silently collide with a requirement the owner wrote, and
`.github/scripts/coverage.sh`, which unions both documents, would read two
different requirements as one. Oracle requirements therefore start at **R1000**,
and the check enforces it.

Plans cover these ids exactly like any other: `covers: [R1000]`.

## Append-only, and superseded rather than revised

A decision that has landed is never edited or removed. When one turns out to be
wrong, write a **new** decision that names the old id and says what replaced it
— the same lifecycle `docs/escapes.md` uses. Ids only ever increase.

This is the rule that stops an oracle quietly revising yesterday's ruling, where
the diff would read as an edit rather than as a reversal.

## The schema

Every decision is a `##` heading with the id, then these eight fields:

    ## OD-<n> — one line saying what was decided

    - **Date:** YYYY-MM-DD
    - **Evidence:** ESC-<n>, BL-<n>
    - **Requirements added:** R1000, R1001   (or "(none)")
    - **Requirements superseded:** R1000     (or "(none)")
    - **Vision statement relied on:** V<n> — "<the FULL sentence, verbatim>"
    - **Vision statements against:** V<n> — "<the statement that most nearly
      forbids this>", and why it does not   (or "(none — no statement in
      docs/VISION.md tells against this)")
    - **Alternatives considered:** what else was weighed, and why not
    - **Rationale:** why this, given that evidence and that statement

    Then any prose the decision needs: the requirement text itself, what it
    changes downstream, which plans it affects.

One field is optional, and it is the only thing written here that changes what
another gate does:

    - **Criterion waived:** S3 — <what the criterion's script does not
      recognise about what was built>

See "Waiving a success criterion" below before writing one.

### The sixth field is what makes the fifth honest

A decision that names only the statement supporting it has not weighed the
vision — it has searched it. The owner reading the ledger cannot tell those
apart, because both produce one quoted sentence. Naming the statement that most
nearly forbids the decision, and saying why it does not, is the difference
between a reading and a justification, and it is the one part of this schema an
agent cannot produce without having read the whole file.

Writing `(none)` there is a claim, and a false one is visible the moment the
owner reads the vision alongside the ledger.

### Quote the whole sentence, and name its id

`.github/scripts/oracle-decisions.sh` reads `docs/VISION.md` at the base commit
and fails a decision whose quoted text is not in it. That closes the hole where
this field's entire validation was the presence of a `"` character — a
one-letter quote passed, in a repository with no vision file at all.

A fragment is rejected for a related reason: one short enough to invert is one
too short to cite. Six words lifted out of *"I would trade any feature for a
design I can hold in my head"* can be made to argue for adding complexity, which
is the opposite of what the sentence says, and the ledger entry reads as a clean
derivation either way.

### If `docs/VISION.md` does not exist

Deleting it is a legitimate choice and it means one specific thing: **this
project has no tiebreaker, so the oracle rules with none.** Every decision then
uses the explicit class —

    - **Vision statement relied on:** (no vision statement decided this)

— which is not a formality here, it is the accurate value. That class already
obliges **Alternatives considered** to say what else was weighed and why it
lost, and with no vision that field is the entire record of the reasoning.

Quoting a sentence from a file that is not in the tree is the one thing that
must not happen, and the check now refuses it. If you find yourself reaching
into git history for a statement, the correct field value is the opt-out.

### The vision field is the point

The other six are bookkeeping. **Vision statement relied on** is what makes the
role steerable rather than merely reviewable: when the owner disagrees with a
decision, they can see exactly which sentence of `docs/VISION.md` produced it
and edit *that*, instead of guessing which of ten statements was doing the work
and arguing with each decision one at a time.

Quote the statement. Do not paraphrase it — a paraphrase is the decision
restating itself, and the check refuses a vision field with neither quotation
marks nor the one explicit opt-out:

    (no vision statement decided this)

That opt-out exists for the ruling class the vision genuinely does not decide —
an uncertainty a plan filed, most often — which otherwise could not be written
at all without paraphrasing a statement into existence. Using it moves the
weight onto **Alternatives considered**: what else was weighed and why it lost,
so the owner can still see what a different vision sentence would have changed.
The check refuses the opt-out with `(none)` there. Guessing is allowed;
guessing silently is not.

## What the check enforces

`.github/scripts/oracle-decisions.sh`, on every pull request:

- every new decision cites evidence that exists at the **base commit**;
- every new decision carries all seven fields, non-empty;
- the vision field either quotes a statement or declares the no-vision class,
  and the class demands real alternatives;
- a decision present at the base commit is neither modified nor removed;
- ids are unique and increasing;
- added requirement ids are at or above R1000;
- at most 150 decisions (a runaway-loop backstop, not a real bound);
- plans under `docs/plans/oracle/` cite a decision that has already landed, or
  cover only requirement ids that already exist in a design document — either
  way a plan there implements landed work, it never proposes any;
- a handoff under `docs/oracle/` is never modified after it is written;
- an optional `**Criterion waived:**` field names at least one `S<n>` and
  carries a reason — see below.

## Waiving a success criterion

`docs/DESIGN.md` §13's criteria are scripts under `acceptance/`, run as a
required check on every pull request
(`.github/scripts/acceptance-criteria.sh`). A failing one is routed here: the
acceptance pass files it as a `BL-<n>`, and the oracle rules on it like any
other logged evidence. Three rulings are available.

- **The test is wrong** — it measures something §13 did not ask for, or measures
  it badly. Record the decision citing the evidence; the script is corrected on
  its own pull request.
- **The implementation is wrong** — back to building. That is the ordinary loop
  doing its job and needs nothing special here.
- **The criterion is met by other means** — the implementation solved the
  problem in a way the script does not recognise. This is the case that needs
  the waiver, because a ruling that leaves the check red unblocks nothing: every
  later pull request stays red and work stops.

So a decision may carry:

    - **Criterion waived:** S3 — <why the script does not recognise what was built>

`acceptance-criteria.sh` reads landed waivers at the base commit and skips that
criterion. Four properties make this an exception rather than a hole:

- **Per-criterion, never per-check.** A waiver on `S3` does nothing for `S4`.
- **Cited, append-only, permanent.** It lives in this ledger, so it inherits
  evidence-citation and immutability for free — no new file and no new trust
  boundary. The same idiom as `docs/escapes.md`: an exception written down
  rather than taken silently.
- **Visible twice**, here and as `pending / owner` in `docs/acceptance.md`. The
  gate goes green; the claim of doneness does not.
- **Self-clearing.** If a later change makes `S3` genuinely pass, the next
  acceptance pass records `pass` and the waiver is moot.

**The oracle may not mark a criterion passed.** It rules, it records, it may
waive — and the row stays `pending / owner`, carrying the reasoning. The owner's
own definition of done is adjudicated by the owner. `docs/acceptance.md` is the
one artifact in an unattended run whose pull request requires their review; if
an agent could rule a failing criterion met, the last checkpoint before the
human becomes something an agent can talk its way past, which is the failure the
whole acceptance mechanism exists to prevent.

A bare waiver with no reasoning is refused by the check. The field is the one
place the oracle sets aside the owner's definition of done, so there has to be
something in it the owner can disagree with.

## The one stop, and it is written down

A decision that would violate a core tenet of `docs/VISION.md` is not made. The
oracle writes a **halt entry** instead — same id sequence, same append-only
rule, a different shape:

    ## OD-<n> — HALTED: <what could not be decided>

    - **Date:** YYYY-MM-DD
    - **Evidence:** ESC-<n>
    - **Tenet relied on:** V<n> — "<the verbatim tenet>"
    - **What a decision would have said:** the ruling that was available
    - **What it needs from the owner:** the smallest change to docs/VISION.md
      that would let this be decided, or the ruling to make directly

A halt does not stop the run — the driver moves to the next phase exactly as it
does today. What it stops is the evidence disappearing. Without an entry here, a
tenet stop and an oracle finding nothing worth acting on produce the same
artifact — no decision — and the delivery driver marks the evidence processed
either way, so the one moment the vision actually did its job is the one moment
nothing records. This ledger is the only append-only document an agent may write
unattended, which is exactly what a halt needs.

Everything else it decides on the evidence it has — it never marks a decision
pending, because a pending decision stops work, which is the failure this whole
arrangement exists to prevent. A halt is not a pending decision: it is a
decision not to decide, recorded.

<!-- Append decisions below, newest at the bottom. Never edit one that has
landed; supersede it with a new decision naming its id. -->

## OD-1 — Results print with at most 12 significant digits (Python `.12g`)

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted." — the nearest reading against is that any formatting rule is machinery a raw `print` would not need. It does not forbid this: the rule is one format specification, the raw float repr is exactly the output that is *not* obviously right (it is ESC-1), and V3 ranks below V1 in any case.
- **Alternatives considered:** shortest-round-trip repr, Python's default —
  rejected: it is the observed defect, `100.00000000000001` presented as a
  result. Fixed decimal places — rejected: values below the cutoff print as
  `0.00`, a confidently wrong number, and R1/R2 span nine orders of magnitude
  (mm to mi, mg to kg). `decimal.Decimal` end to end — rejected: heavier
  machinery than one format call, and §8's affine temperature functions route
  through binary floats anyway, so the artifact class survives. 15 significant
  digits — rejected: doubles carry 15–17, so error accumulated across the §8
  base-unit hub's two multiplications can still surface in the last printed
  digit; 12 leaves a guard band while exceeding any precision a hand-typed
  conversion carries.
- **Rationale:** ESC-1 is a floating-point artifact presented as a result, and
  `docs/DESIGN.md` §11 explicitly left the precision rule undecided pending
  logged evidence. Rounding to 12 significant digits removes the artifact
  class wholesale — every decimal-exact conversion prints its short form —
  without truncating small magnitudes to zero, and it is a single, testable
  sentence of behaviour. Confidence is high: any reasonable significant-digit
  count in the 10–14 band would do, and superseding this with a different
  count later costs one entry.

**R1000** — A printed conversion result carries at most 12 significant digits,
with the formatting behaviour of Python's format spec `.12g`: no padded
trailing zeros, a value whose rounded form is integral prints without a
decimal point, and extreme magnitudes may use scientific notation. The ESC-1
case is normative: `0.1 km` to metres prints exactly `100`, never
`100.00000000000001`. *Evidenced by:* S1, S2.

The measurement is part of this decision (`docs/VISION.md`, "Durable evidence
is a requirement, not a nicety": a change nothing can observe is a change
nobody can evaluate). No new mechanism is needed — the acceptance scripts are
the existing instrument. The plan implementing R1000 must make
`acceptance/S1.sh` compare printed text exactly, byte for byte rather than
numerically within a tolerance, and include the ESC-1 case in its fixed
table; and make `acceptance/S2.sh` assert the round trip returns the printed
start value, not merely a close one. Once that script has been observed red
against unformatted repr output and green against the fix, the completing
correction row for ESC-1 is appended to `docs/escapes.md` by the work that
lands it.

Downstream: no plan exists yet (`docs/plans/` holds only the template), so no
existing plan is touched; the milestone `convert` plan must list R1000 in its
`covers:` and build the formatting into the same print path S1 exercises.

## OD-2 — HALTED: BL-3, aligned colored output via the `rich` library

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Tenet relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet."
- **What a decision would have said:** Granting BL-3 as filed adds `rich` as a
  runtime dependency, which V5 forbids in those exact words and R8 repeats in
  the design. The only tenet-respecting rulings available were to refuse an
  item the owner filed, or to rewrite it as stdlib-only aligned output — which
  BL-3's own text pre-rejects ("using the `rich` library specifically",
  "hand-rolling ANSI codes is wasted effort"). The owner's proposal and the
  owner's tenet contradict each other, and that is not a tie the oracle
  breaks.
- **What it needs from the owner:** the smallest `docs/VISION.md` change that
  would let this be decided is an exception clause in V5 (for example,
  permitting a named output-formatting dependency), landed with the matching
  amendment to R8. Alternatively rule directly: append a backlog line
  withdrawing BL-3, or append one restating it as stdlib-only formatting, and
  the next oracle run decides it under the tenet as it stands.

## OD-3 — BL-4, live currency conversion, is rejected; the design's non-goal stands

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce." — and V4 — "Breadth of units is expendable: dropping exotic units, aliases, or whole categories is always an acceptable price for correctness, clarity, or simplicity."
- **Vision statements against:** (none — no statement in docs/VISION.md tells against this; every priority statement ranks something above breadth, and the nearest candidate, V4, argues for the rejection rather than against it)
- **Alternatives considered:** granting it with a stdlib-only fetch via
  `urllib`, which would survive V5 — rejected: R8 requires fully offline and
  deterministic, §3 names "any unit that needs live data" a non-goal, and a
  rate arriving over the network is a number whose correctness the tool cannot
  vouch for; a stale or failed fetch is a wrong number presented confidently.
  Bundling a static rate table to stay offline — rejected: an exchange rate
  hardcoded at commit time is wrong by construction within days, the exact
  shape V6 rejects outright. Halting for the owner — not available: no core
  tenet blocks this ruling, and the owner's own approved design already
  decides it.
- **Rationale:** BL-4 contradicts the design rather than exposing a gap in it:
  `docs/DESIGN.md` §3 lists currency and live-data units as non-goals and R8
  requires offline, deterministic behaviour. The vision breaks the tie the
  same way the design already ruled, so the design stands unchanged. The item
  stays in Proposed, where only the owner moves it; the steering lever for
  wanting currency anyway is `docs/DESIGN.md` itself, which is owner-landed.
