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

## OD-1 — Printed results carry at most 12 significant digits, ending the floating-point artifact

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce." — and, for the measurement this decision carries, the durable-evidence ruling: "A change nothing can observe is a change nobody can evaluate."
- **Vision statements against:** V6 — "A conversion that is numerically wrong, however plausible it looks, is rejected outright — as is any run that reports success while a criterion's evidence cell is empty or narrated rather than executed." It does not forbid this: rounding to 12 significant digits discards only binary floating-point representation noise, never measured information — the mathematically exact answer to 0.1 km in metres is exactly 100, and this rule prints that where the unrounded float printed the artifact. The rounding moves every printed number toward the true value, never away from it.
- **Alternatives considered:** Shortest round-trip repr (Python's default str(float)) — prints the ESC-1 artifact verbatim, i.e. the defect is its defined behaviour. Fixed decimal places (two, or six) — wrong across magnitudes: 1 mm in km becomes a confidently wrong 0.00, exactly the output V1 calls worst. decimal.Decimal arithmetic — standard library, so V5-clean, but factors like 1/0.3048 are not finite decimals, so a rounding rule is still needed at the end and the extra machinery removes nothing (V3). 15–17 significant digits — inside double precision's noise band, where the ESC-1 class recurs after two chained operations.
- **Rationale:** Twelve significant digits exceeds the precision of anything a unit converter is used for, while sitting three to four digits below where double-precision noise appears after the two multiplications a base-unit-hub conversion performs (docs/DESIGN.md §8). It is one standard-library call, strips trailing zeros, and needs no per-unit tuning. Confidence is high for the artifact class ESC-1 logged; the exact digit count (12 rather than 10 or 14) is a judgment call, recorded here precisely so it can be superseded cheaply if real output ever argues for another count.

**R1000** — Every numeric conversion result `anvil` prints is formatted with
Python's `format(value, ".12g")`: at most 12 significant digits, trailing zeros
stripped, scientific notation only when the `g` conversion produces it, and no
other rounding, padding, or locale formatting anywhere on the output path. In
particular, converting 0.1 km to m prints exactly `100`, and the S2 fixtures
print exactly `212` and `373.15`.

The measurement is part of this decision, per the vision's durable-evidence
section, and it uses existing mechanisms rather than inventing one. The plan
that covers R1000 must make the rule observable twice: unit tests asserting
exact printed strings — including the ESC-1 reproduction, 0.1 km → m prints
`100` — red against the artifact and green against the fix; and the acceptance
scripts for S1 and S2 comparing the installed command's exact stdout strings,
with the 0.1 km → m row in S1's fixed table. Comparing exact strings rather
than parsing floats back is the point — a numeric comparison would accept the
artifact ESC-1 logged. Once fix and check have merged, the implementing pull
request's author appends the ESC-1 correction row in docs/escapes.md naming
the demonstrated check; that ledger is not the oracle's to write.

Downstream: this resolves the first open question in docs/DESIGN.md §11
(output precision, deliberately left open there). The other two §11 questions
— exact CLI syntax and the batch line format — remain open and are not decided
here; the planner files them as uncertainties when planning reaches them. No
plans exist yet, so none are invalidated.

## OD-2 — BL-3 declined: no rich, no table output — results stay plain standard-library text

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet." — and V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** (none — no statement in docs/VISION.md tells against this. The vision prizes correct numbers, honest errors, and simplicity; nothing in it speaks for richer presentation. The nearest candidate, V2's mention of feature breadth, ranks breadth below clarity of errors, which argues in this decline's direction rather than against it.)
- **Alternatives considered:** Adopting rich as BL-3 asks — a diff adding it is what V5 defines as a tenet violation, and AGENTS.md additionally requires owner approval landed as a repository artifact before any dependency merges, which no unattended agent can obtain. Hand-rolled ANSI alignment in the standard library — V5-clean, but BL-3 itself calls hand-rolling wasted effort, and a tool that prints one value per invocation (or per stdin line, R6) has nothing to tabulate, so it fails V3 with no gain. A HALT entry — rejected: a halt records a ruling a tenet forbade the oracle to make, and the ruling available here is the tenet applied, not the tenet violated; declining is a decision, and it was made.
- **Rationale:** BL-3 sits in Proposed, filed by the owner but never approved (docs/BACKLOG.approved.md records nothing), while V5 is an owner-landed core tenet in the CODEOWNERS-owned tiebreaker. Between an owner's unapproved idea and the owner's landed tenet, the tenet rules — that is what the tiebreaker is for. If the owner wants this, the steer is editing V5 (for example, carving out display-only dependencies) and superseding this decision. Declining changes no behaviour, so no new measurement is owed: the invariant this keeps is already observed — plan-metrics.sh detects an added dependency mechanically, and R8's stdlib-only requirement is evidenced by S4.

## OD-3 — BL-4 declined: no currency conversion — the design's live-data non-goal stands

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** the purpose statement (unnumbered, under "What this project is for") — "grimsverk-anvil exists to prove, on a real overnight run, that the grimsverk-template pipeline works end to end — and, as a side effect, to leave behind a small unit-conversion CLI that answers instantly and offline." — and V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently." It is the only sentence that treats feature breadth as a value at all, and it subordinates breadth to exactly the behaviour declining preserves: a currency symbol today refuses loudly with an unknown-unit error (R4, evidenced by S3), where a currency mode built on fetched rates would answer with a number the tool cannot verify.
- **Alternatives considered:** Live rates over stdlib urllib — no new dependency, so V5-clean, but it breaks R8 ("fully offline and deterministic"), the offline purpose sentence above, and the test suite's offline rule; a rate fetched at run time is a number the tool must present on trust, and V1 calls a wrong number presented confidently the worst possible output. Bundled static rates — strictly worse: silently stale from the day they land, the confidently-wrong shape with no network to even blame. Granting BL-4 as a design change — not the oracle's to grant: docs/DESIGN.md §3 lists currency and live data as an explicit non-goal, that document is owner-landed, and overturning an owner-landed non-goal on the strength of an unapproved Proposed item would be the oracle rewriting the design rather than correcting it from evidence.
- **Rationale:** BL-4 does not report the design wrong anywhere reality tested it — no escape, no failing criterion — it wishes the design were bigger, and the design already answers it: currency is a named non-goal. The evidence is metabolised by recording that the non-goal stands. Declining changes no behaviour, so no new measurement is owed; the behaviour the decline preserves is already measured, because S3's unknown-unit case is precisely the loud refusal a currency symbol produces today. If the owner wants currency, the steer is editing docs/DESIGN.md §3 and §5, which only they can land.
