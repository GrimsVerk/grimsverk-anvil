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

## OD-1 — Converted values print with at most 12 significant digits (`.12g`)

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently." Rounding could be read as silently discarding information, but the seventeenth significant digit of `100.00000000000001` is not information about the conversion — it is information about IEEE-754 binary representation, and printing it is exactly the confidently wrong number V1 rejects. Nothing is guessed: the arithmetic is unchanged; only the rendering is bounded.
- **Alternatives considered:** (1) Print the float unrounded — that is the defect ESC-1 records, not a resolution of it. (2) A fixed number of decimal places — scales badly across magnitudes: two decimals erases 1 mm expressed in km (`0.00`), while twelve decimals reintroduces the artifact on large values; significant digits scale with the value, decimal places do not. (3) Exact `decimal`-module arithmetic — heavier machinery than one formatting call, and factors like ft→m are not exact decimals anyway, so the artifact would move rather than disappear. (4) Fewer significant digits, e.g. six — throws away genuine precision a script consumer may need; twelve keeps every digit a physical measurement could plausibly carry while sitting well below the 15–17-digit region where binary representation noise lives.
- **Rationale:** ESC-1 is §11's deliberately undecided precision question producing a wrong-looking number on the very first hand run: 0.1 km rendered as `100.00000000000001` metres. One standard-library formatting call resolves it: `format(value, ".12g")` suppresses representation noise (0.1 km → `100`), never pads with false zeros, and preserves twelve significant digits of genuine result. Confidence is high that `.12g` removes this class of artifact; the choice of twelve over ten or fourteen is judgment, recorded here so superseding it costs one entry if evidence arrives.

**R1000** — Output precision: every converted value, in one-shot and batch mode
alike, is rendered with Python's `.12g` format — at most 12 significant digits,
trailing zeros stripped — so `0.1 km` in metres prints exactly `100` and never
`100.00000000000001`. Error messages and usage text are unaffected.

Measurement, per the vision's durable-evidence section ("A change nothing can
observe is a change nobody can evaluate"): the plan that implements R1000 must
(a) include the ESC-1 case in `acceptance/S1.sh`'s fixed conversion table —
`0.1 km` to `m` expecting exactly `100` — and (b) carry unit tests asserting the
`.12g` rule on at least one value that would otherwise show representation
noise. `acceptance/S1.sh` does not exist yet; the milestone plan that creates it
carries this case from the start. Once that script has merged and been observed
red-then-green, ESC-1's stub in `docs/escapes.md` gets its completing correction
row naming it.

Downstream: no plans exist yet, so R1000 folds into the first milestone plan
(`convert`, covering R1, R2, R4, R5) rather than needing a separate steward
plan — it is one formatting call plus its tests.

## OD-2 — Currency conversion is declined; the design's offline non-goal stands

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted." — and the purpose statement: "grimsverk-anvil exists to prove, on a real overnight run, that the grimsverk-template pipeline works end to end — and, as a side effect, to leave behind a small unit-conversion CLI that answers instantly and offline."
- **Vision statements against:** (none — no statement in docs/VISION.md tells against declining this; the nearest candidate, the purpose sentence's end-to-end ambition, does not require building every filed proposal — declining one through this ledger exercises the pipeline exactly as building one would — and V4, breadth of units being expendable, points the same way as this ruling.)
- **Alternatives considered:** (1) Currency with pinned or cached rates, keeping the tool offline — still the thing §3 names a non-goal ("Currency, time zones, or any unit that needs live data"), and pinned rates make confidently wrong money numbers within days, the exact failure V1 ranks worst. (2) Live fetching via the standard library's `urllib` — adds no package, so core tenet V5 is technically untouched, but it breaks R8's "fully offline and deterministic", makes output depend on a network endpoint nobody here controls, and makes results non-reproducible, which no test in this suite could verify offline. (3) Decline and leave the design as it stands — chosen.
- **Rationale:** BL-4 asks for the one feature the owner's own design lists as a non-goal, and the vision's purpose sentence ends "answers instantly and offline". "Feels half-finished" is completeness pressure, and V3 ranks simplicity above completeness explicitly. This decision changes no behaviour, so no new measurement is owed — there is nothing to observe that existing gates do not already cover. BL-4 stays in Proposed as text, resolved by this citation; if the owner wants currency, that is a change to `docs/DESIGN.md` §3, which is theirs to land.

## OD-3 — HALTED: prettier output via the `rich` library (BL-3)

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Tenet relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet."
- **What a decision would have said:** Aligned, readable output built with the standard library alone — `str.format` field widths for alignment, colour omitted or emitted only on a tty. But BL-3 names `rich` specifically and explicitly rejects hand-rolled ANSI as wasted effort, so every available ruling either adds a runtime dependency, which the tenet forbids outright, or countermands the owner's explicit instruction in the evidence, which is not the oracle's call to make.
- **What it needs from the owner:** The smallest change to `docs/VISION.md`: amend V5 with an explicit carve-out (for example, "display-only dependencies the owner names in docs/DECISIONS.md are exempt"). Alternatively, rule directly: either approve `rich` per the Dependencies rule in `AGENTS.md` (a `docs/DECISIONS.md` entry landed before the dependency merges), or refile the request without naming `rich`, at which point a standard-library formatting decision can be made on the ordinary path.
