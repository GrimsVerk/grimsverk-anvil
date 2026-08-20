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

## OD-1 — Results print at most 12 significant digits; float artifacts are a defect, not output

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V6 — "A conversion that is numerically wrong, however plausible it looks, is rejected outright — as is any run that reports success while a criterion's evidence cell is empty or narrated rather than executed." It can be read to forbid any rounding at all, since a rounded value is not the bit-exact float the converter computed. It does not: the bit-exact float is itself an approximation of the true decimal answer, and `100.00000000000001` for 0.1 km in metres is that approximation's error leaking into the output — the digits the rule below removes are exactly the wrong ones, and printing them is what V6 rejects.
- **Alternatives considered:** (a) shortest round-trip repr — the status quo, and the defect ESC-1 logged; (b) a fixed count of decimal places — pads whole-number results with false precision and truncates small ones (0.001 mm in km has no digits left at two decimal places); (c) exact decimal arithmetic end to end via the `decimal` module — heavier machinery that still needs a display rule at the end, because factors such as ft→m produce non-terminating quotients, so it adds complexity without removing the decision; (d) 6 significant digits, the `%g` default — discards real precision from results scripts may pipe onward, against V1. Twelve significant digits keeps every digit this table's arithmetic can vouch for and drops the ones it cannot.
- **Rationale:** IEEE-754 doubles carry 15–17 significant decimal digits, and the artifact ESC-1 observed lives in the last one or two of them; a conversion here is a handful of multiplications and at most one addition, so the first twelve digits of the rounded result are digits of the true answer. Rounding the *display* to 12 significant digits therefore removes only wrong digits — V1's "wrong number presented confidently" — while changing no computed value. Confidence: high on the shape of the rule, moderate on the exact figure 12; if that figure is wrong, superseding it costs one entry.

**R1000 — Output precision.** A converted result is printed rounded to at most
12 significant digits, with trailing zeros (and a bare trailing decimal point)
stripped — `g`-style formatting, so magnitudes outside that shape may use
exponent notation. Consequences: 0.1 km to m prints `100`, never
`100.00000000000001`; 100 C to F prints `212`; a result of 373.15 prints
`373.15`.

**Measurement, per the durable-evidence ruling in `docs/VISION.md`.** No new
collection mechanism is needed — two existing ones observe this behaviour once
the case is in them, and the plan that implements R1000 carries both: (1) the
fixed table `acceptance/S1.sh` checks must include the ESC-1 case — 0.1 km to
metres printing exactly `100` — so the rule is exercised through the installed
command on every pull request; (2) the test suite gains a unit test for the
formatting rule, demonstrated red against the unrounded output and green
against the fix. Once both have merged, the ESC-1 correction row is appended to
`docs/escapes.md` naming the demonstrated check.

## OD-2 — BL-3 rejected: no `rich`, no table output; results stay plain single-line text

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet." and V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently." is the nearest, if aligned tables are read as a form of clarity. It does not forbid this: it names errors, not result formatting, and it ranks breadth below clarity — and for the script authors §4 of `docs/DESIGN.md` names, a plain deterministic line *is* the clear output, while ANSI-decorated tables are what breaks their pipes.
- **Alternatives considered:** (a) adopt `rich`, as BL-3 asks — a runtime dependency, which the vision's one core tenet forbids outright; (b) hand-rolled ANSI tables — stdlib-legal, but BL-3 itself calls that wasted effort, and any table output breaks the one-result-line-per-request shape R6 promises batch callers; (c) reject and keep plain text — chosen. This is a rejection rather than a halt: a tenet-compliant ruling existed, and V3 would have rejected the feature even with V5 deleted, so no decision violating a tenet was ever on the table.
- **Rationale:** BL-3 names, as its only acceptable means, exactly the thing V5 exists to forbid, and its end — prettier output — is completeness, which V3 ranks below simplicity and which nothing in the vision ranks above anything. The item is owner-filed, but it sits in Proposed, and the vision is the tiebreaker the owner made supreme: a pipeline that adopted `rich` overnight on the strength of a backlog suggestion would be overriding the owner's only core tenet on the owner's own prompt. If the owner wants this feature, the price is one edit to V5 — that edit, not a superseding oracle decision, is the designed reversal path.

## OD-3 — BL-4 rejected: currency stays a non-goal; no live data at run time

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** (none — no statement in docs/VISION.md tells against this; the only mention of feature breadth, in V2, ranks it below clarity of errors, and V4 offers breadth as the first thing to trade away)
- **Alternatives considered:** (a) live rates fetched over the network — possible with `urllib` and no new dependency, so V5 is not the obstacle; the design is: §3 of `docs/DESIGN.md` names currency and live-data units a non-goal, R8 requires the tool fully offline and deterministic, and a fetched rate is a number no offline test, acceptance script, or the owner's own no-network S4 check can ever verify, so V1's worst output becomes routine; (b) baked-in fixed rates — offline, but an exchange rate goes stale the day it is committed, and a stale rate is precisely a wrong number presented confidently, worse than refusing; (c) reject — chosen: a currency symbol stays an unknown unit and gets R4's loud error.
- **Rationale:** The design already decided this — currency is a named non-goal and R8 makes the tool offline and deterministic — so this ruling restates the design rather than amends it; the entry exists so BL-4 is resolved on the record instead of resurfacing as unprocessed evidence every run. An exchange rate is not a conversion factor: it is time-varying data, and a converter whose answers change by the hour cannot satisfy a suite, an acceptance script, or V1. Reversing this belongs to the owner, by editing §3 and R8 of `docs/DESIGN.md`, which are theirs.
