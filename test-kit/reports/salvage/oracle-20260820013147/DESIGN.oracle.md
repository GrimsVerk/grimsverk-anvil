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

## OD-1 — Results print at 12 significant digits, so float artifacts never reach output

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V6 — "A conversion that is numerically wrong, however plausible it looks, is rejected outright — as is any run that reports success while a criterion's evidence cell is empty or narrated rather than executed." Rounding discards digits, and discarding digits could be read as making the printed number numerically wrong. It does not: the digits discarded are binary floating-point noise beyond the precision of every factor in the unit table, and the artifact ESC-1 records — `100.00000000000001` for an exact 100 — is itself the numerically wrong presentation. The rounded value is closer to the true result, not further from it.
- **Alternatives considered:** (1) Shortest round-trip repr, Python's default float printing — rejected: it is what produced ESC-1, because `100.00000000000001` is the shortest string that round-trips that float. (2) A fixed count of decimal places, e.g. always six — rejected: it pads exact results to `100.000000`, flattens small magnitudes toward zero, and adds nothing for large ones; significant digits scale with magnitude, decimal places do not. (3) Decimal arithmetic end-to-end — rejected: it removes binary artifacts at the source but rewrites the converter and every factor to fix a presentation defect a one-line formatter fixes, against V3's simplicity ranking. (4) Fifteen significant digits — rejected: chained conversions through a base unit can accumulate error into the fifteenth digit; twelve leaves a safety margin while still exceeding the certified precision of every factor the design names.
- **Rationale:** §11 of `docs/DESIGN.md` deliberately left output precision undecided, and ESC-1 is the logged evidence that undecided precision produces a confidently wrong-looking number. Twelve significant digits is far more precision than any conversion factor in §5 carries, and far less than where float artifacts live, so it prints every honest digit and none of the noise. Confidence is high on the shape (significant digits, not decimal places) and moderate on the count; if twelve proves wrong in either direction, superseding this costs one entry.

**R1000** — Every result value `anvil` prints — single-shot, and each batch
result line — is formatted with Python's `format(value, '.12g')`: at most 12
significant digits, correctly rounded, trailing zeros stripped, `g`-style
exponent notation where 12 significant digits cannot render the magnitude
plainly. In particular `anvil 0.1 km m` prints `100`, never
`100.00000000000001`.

This decides only §11's precision question. The command-line syntax and the
batch line format stay open, for planning to file uncertainties on as
`AGENTS.md` requires.

Measurement, per the durable-evidence section of `docs/VISION.md` ("When a
decision alters behaviour that no existing check, test, run report or review
artifact would notice, adding the thing that notices is part of the decision —
not a follow-up, and not optional"): no measurement of output formatting exists
today, so the plan implementing R1000 carries two. First, blind tests asserting
the exact printed string for the ESC-1 case and for boundary cases (an exact
integer result, a sub-unity result, a temperature). Second, the fixed table in
`acceptance/S1.sh` — the S1 criterion covers R1, and `0.1 km` to `m` is a
length conversion — must include that case expecting the exact string `100`.
That is the "acceptance script" ESC-1's pending check column asks for, without
minting a new criterion id, which only the owner may do in §13. Once the check
has been observed red against the defect and green against the fix, the
implementing work appends ESC-1's correction row in `docs/escapes.md`.

## OD-2 — Currency conversion declined; the design's offline non-goal stands

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** (none — no statement in docs/VISION.md tells against this; the nearest candidates both point the same way as the decision: V2 ranks clear errors above feature breadth, and V4 declares breadth of units expendable for exactly the qualities live currency data would cost.)
- **Alternatives considered:** (1) Live rates fetched with stdlib `urllib` — no new dependency, so V5 untouched — rejected: R8 requires fully offline and deterministic, §3 names "Currency, time zones, or any unit that needs live data" a non-goal, and a result that varies with the network is one no offline acceptance script can pin. (2) A bundled static rate table — rejected: exchange rates decay in hours, so a stale rate presented as a conversion is V1's "wrong number presented confidently", the worst output this tool can produce. (3) Accepting BL-4 and adding a requirement — rejected: it would use a Proposed backlog item to overrule the owner's own design document, inverting the authority order this repository is built on.
- **Rationale:** BL-4 argues from completeness — "a converter that cannot do money feels half-finished" — and V3 ranks simplicity above completeness by name. The design already decided this question in §3 and R8; the evidence adds a preference, not a fact that contradicts the design, so the design stands. No requirement is added and no plan follows. If the owner wants currency, the move is theirs and it is two edits, both owner-landed: §3/R8 in `docs/DESIGN.md`, and the priority order in `docs/VISION.md`. This decision changes no behaviour, so no new measurement is owed.

## OD-3 — HALTED: BL-3's pretty tables require the `rich` dependency V5 forbids

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Tenet relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet."
- **What a decision would have said:** Add a requirement that results print as aligned, colored tables rendered by the `rich` library, and hand it to planning. BL-3 admits no narrower reading: it names `rich` "specifically" and calls hand-rolling ANSI codes "wasted effort", so a stdlib-only variant would not be a ruling on this evidence but a substitution of it.
- **What it needs from the owner:** One edit, in either direction. To get BL-3: amend V5 in `docs/VISION.md` with a carve-out — for example, naming display-only dependencies the owner exempts — and the next oracle run decides BL-3 under the amended tenet. To keep V5: file a new backlog item superseding BL-3 that asks for readable output achievable with the standard library, which the oracle can then weigh under V2 and V3 — or simply leave BL-3 where it sits, in Proposed, where nothing builds it unprompted. As filed, BL-3 and V5 cannot both be honoured, and a core tenet outranks a proposal.
