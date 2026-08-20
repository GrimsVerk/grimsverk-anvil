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

## OD-1 — Results print with at most 12 significant digits, via Python's `.12g` format; float artifacts never reach output

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V6 — "A conversion that is numerically wrong, however plausible it looks, is rejected outright — as is any run that reports success while a criterion's evidence cell is empty or narrated rather than executed." — it can be read as forbidding any rounding at all, since rounding discards digits. It does not: the digits beyond the twelfth significant place of a two-multiplication double-precision chain are representation noise, not computed signal, so `100.00000000000001` for 0.1 km in metres is itself the confidently wrong number V6 rejects, and printing fewer digits than the noise floor is what removes it.
- **Alternatives considered:** shortest-round-trip formatting (`repr`) — reproduces ESC-1 verbatim, rejected; a fixed count of decimal places (2 or 6) — truncates small correct results toward zero (0.0000015 m becomes 0.00), which is a wrong number under V1, rejected; `decimal.Decimal` arithmetic throughout — stdlib-legal but a second numeric model for a three-category converter, still needing a print rule at the end, so it adds machinery without removing the decision, rejected under V3; 15–17 significant digits — inside the double-precision artifact zone, would still print ESC-1's tail, rejected.
- **Rationale:** ESC-1 is logged evidence that the design's undecided output-precision question produces confidently wrong-looking numbers, and §13's S1/S2 expect exact values, which presupposes a defined output format — the criteria are unwritable as scripts until a rule exists. Twelve significant digits keeps every digit the computation can vouch for (conversions here are one or two double-precision multiplications, accurate to well beyond 12 significant digits) while sitting safely below the ~15–17 digit zone where binary representation noise appears. `format(value, ".12g")` is one deterministic standard-library call, satisfying V3 and V5 in passing.

**R1000** — Every numeric result line, single-shot and batch alike, is printed as Python's `format(value, ".12g")`: at most 12 significant digits, no trailing zeros, exponent form only when `g` selects it. In particular 0.1 km converted to metres prints exactly `100`. Error and usage messages are not results and are unaffected.

Measurement, which is part of this decision (docs/VISION.md, durable evidence: "A change nothing can observe is a change nobody can evaluate."): the plan that implements R1000 must (a) include the ESC-1 reproduction in `acceptance/S1.sh`'s fixed table — 0.1 km to metres, expected stdout exactly `100`, compared as an exact string — and (b) carry unit tests asserting the `.12g` formatting on the result path. Once that script has been observed red against the defect and green against the fix, append the ESC-1 correction row in docs/escapes.md and the closure row in docs/escapes.done.md naming `acceptance/S1.sh`; ESC-1's check column already promises exactly this shape.

## OD-2 — BL-3 declined: no `rich`, no table output; results stay plain single-line text

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet."
- **Vision statements against:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently." — the nearest thing to a mandate for better presentation, but it is about error clarity and loud refusal, not decoration of successful output, and nothing in it requires alignment or colour; no other statement values presentation at all.
- **Alternatives considered:** adopt `rich` as filed — the exact diff V5 names as a violation, and nothing in the logged evidence makes a dependency necessary for correctness, clarity, or simplicity, so this is a decline on the merits rather than a tenet halt; hand-rolled ANSI tables in the standard library — V5-legal, but BL-3 itself calls hand-rolling wasted effort, single-shot output is one value with no table to align, and V3 ranks a small obviously-right tool above presentation machinery, rejected; decorated output in batch mode only — batch exists for script authors piping lines (R6, §4), where colour and alignment are actively hostile, rejected.
- **Rationale:** BL-3's ask is a runtime dependency, which V5 — the vision's only core tenet — forbids outright, and the fallback of stdlib table-rendering fails V3 and V4 on its own: presentation breadth is precisely the kind of feature the owner has declared always tradable for simplicity. Output stays the plain single-line form R1000 defines, which the S1/S2/S5 acceptance scripts already observe, so no behaviour changes and no new measurement is needed. This is not a halt: a halt records a ruling the oracle would otherwise have made but a tenet forbids, and no reading of this evidence makes `rich` the right call. If the owner wants rich output, the steering move is editing V5, after which a re-filed item can be ruled on differently.

## OD-3 — BL-4 declined: no currency and no live data; the tool stays offline and deterministic

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce." and V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** (none — no numbered statement tells against this); the nearest is the purpose statement's "a small unit-conversion CLI that answers instantly and offline", whose "unit-conversion" could be stretched to include money, but the same sentence's "answers instantly and offline" is exactly what live rates break, so it tells for declining, not against.
- **Alternatives considered:** live rates via stdlib `urllib` (no new package, so V5 untouched) — still network at runtime, contradicting R8 ("fully offline and deterministic") and §3's explicit non-goal ("Currency, time zones, or any unit that needs live data"), and unverifiable by an offline acceptance script, rejected; baked-in fixed rates — offline, but a rate is time-varying by nature, so within days the tool prints a confidently wrong number, the exact output V1 and V6 reject, rejected; a user-supplied rate argument — no longer currency conversion, just multiplication, surface without a §4 use case, rejected under V3.
- **Rationale:** BL-4 asks the oracle to reverse a decision the owner already recorded in an owner-owned document — §3 names "any unit that needs live data" a non-goal and R8 requires fully offline, deterministic operation — on the strength of "feels half-finished", which is a completeness argument, and V3 ranks simplicity above completeness while V4 prices dropping whole categories as always acceptable. Every implementable variant is either not offline or not correct over time. Declined; the design stands unchanged, no behaviour changes, so no new measurement is needed. Reversing this belongs to the owner as an edit to docs/DESIGN.md §3 and R8, not to an oracle decision.
