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

## OD-1 — Printed results carry at most 12 significant digits

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V6 — "A conversion that is numerically wrong, however plausible it looks, is rejected outright — as is any run that reports success while a criterion's evidence cell is empty or narrated rather than executed." Read strictly it could forbid printing anything other than the exact computed value. It does not: the exact value of 0.1 km in metres IS 100, and `100.00000000000001` is the binary representation's noise presented as if it were a result. Formatting to 12 significant digits moves output toward the mathematically exact answer in every case a factor chain perturbs, so V6 argues for this rule once the whole sentence is read.
- **Alternatives considered:** (a) Print the full `repr` of the float — rejected: it is the defect ESC-1 records, verbatim. (b) 15–17 significant digits — rejected: chained factor conversions (value × to-base × from-base) perturb the last one or two digits of a double, so artifacts would still surface; 12 leaves a safety margin while exceeding the precision of any input a terminal user or script plausibly supplies. (c) A fixed number of decimal places — rejected: no single count serves both `mg→kg` and `km→mm`; small results collapse to `0.00` and large ones carry noise digits. (d) Exact `decimal.Decimal` arithmetic — rejected: heavier machinery across the whole converter for a problem the output boundary solves in one line; V3's simplicity-first ("a small tool that is obviously right") tells against it.
- **Rationale:** ESC-1 logged a floating-point artifact shown as a result, and `docs/DESIGN.md` §11 deliberately left precision undecided, so nothing defined it as a defect. This decision defines it: an artifact digit is a wrong number presented confidently — V1's worst output — and the fix is a single deterministic formatting rule at the output boundary, not a change to the conversion math.

**R1000** — A printed result carries at most 12 significant digits: output is
the shortest form produced by Python's `format(value, '.12g')` — trailing zeros
trimmed, scientific notation for extreme magnitudes — applied identically
everywhere a converted value is printed (one-shot and batch mode). Internal
arithmetic stays binary floating point; only presentation is defined here.
*Evidenced by:* S1.

**The measurement is part of this decision** (`docs/VISION.md`, durable
evidence: "When a decision alters behaviour that no existing check, test, run
report or review artifact would notice, adding the thing that notices is part
of the decision — not a follow-up, and not optional."). No new mechanism is
needed — S1's fixed conversion table is the existing mechanism, and the plan
that implements R1000 must carry two things: the ESC-1 reproducer as a table
row in `acceptance/S1.sh` (0.1 km to m prints exactly `100` — red against the
artifact, green against this rule), and unit tests asserting the formatting
rule at representative magnitudes. Once both have merged, ESC-1's completing
correction row in `docs/escapes.md` names them, closing its pending check
column exactly as it asked ("whatever precision rule the design layer settles,
expressed as an acceptance script").

## OD-2 — Currency conversion stays out; BL-4 is declined and the design's non-goal stands

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** (none — no statement in docs/VISION.md tells against declining this: every priority statement trades breadth away, V4 makes dropping whole categories an acceptable price outright, and the purpose section calls the tool "offline" in so many words)
- **Alternatives considered:** (a) Add EUR/USD/SEK with live rates as BL-4 asks — rejected: it contradicts R8 ("fully offline and deterministic") and §3's explicit non-goal ("Currency, time zones, or any unit that needs live data"), makes results non-reproducible between runs, and a stale or mis-fetched rate is precisely the confidently wrong number V1 names as the worst output this tool can produce. (b) Currency from a fixed offline rate table — rejected: a hardcoded exchange rate is wrong the day after it lands, converting the tool from "obviously right" to "must be trusted", the exact trade V3 forbids; V4's willingness to drop whole categories covers a category that cannot be correct offline a fortiori. (c) Supersede R8 and the non-goal to admit the feature — rejected: both are owner-authored decisions in `docs/DESIGN.md`, and reversing an explicit owner decision is not metabolising evidence of a defect; the path for that reversal is the owner editing their own document, which stays theirs.
- **Rationale:** BL-4 is owner-filed evidence that the tool "feels half-finished" without money, but every constraint that would have to break to admit it — offline, deterministic, dependency-free-of-live-data — is one the owner wrote more deliberately than the backlog line: as a requirement, a non-goal, and the purpose sentence. The design stands; no requirements change; the backlog item is resolved by this decision rather than by work. If the owner wants currency, the move is theirs: edit `docs/DESIGN.md` §3 and §5, and the vision's offline framing with it.

## OD-3 — HALTED: BL-3 asks for `rich`-rendered output, and no ruling can grant it without breaking the no-dependency tenet

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Tenet relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet."
- **What a decision would have said:** The only ruling BL-3 leaves open is "adopt `rich` and add a requirement for aligned, colored table output" — the item names the library specifically and rules out hand-rolled ANSI as wasted effort. That ruling adds a runtime dependency, which V5 forbids in exactly those words. A stdlib-only compromise (plain aligned columns via `str.format`, no color) was available and would not violate V5, but it decides something the evidence explicitly declined to ask for, and would read as resolving BL-3 while leaving its actual ask — `rich` specifically — silently overruled by an agent.
- **What it needs from the owner:** This is an owner-vs-owner conflict — the owner filed BL-3 and the owner wrote V5 — which is why no agent should pick the winner. The smallest change to `docs/VISION.md` that unblocks a decision: append an exception clause to V5 naming the display-only dependencies the owner permits (and land the `docs/DECISIONS.md` dependency approval `AGENTS.md` requires alongside it). Alternatively, rule the other way at no cost to the vision: append a new backlog item superseding BL-3 that asks for prettier output within the standard library, and a future decision here can grant it.

## OD-4 — R1000 is carried by the `convert` milestone plan; no steward plan is cut for OD-1

- **Date:** 2026-08-20
- **Evidence:** BL-5
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** (no vision statement decided this)
- **Vision statements against:** (none — no statement in docs/VISION.md speaks to which plan document carries a requirement; the vision decides what the tool is, and both candidate shapes build the identical tool. The weighing that matters is recorded under Alternatives.)
- **Alternatives considered:** (a) Fold R1000 into the `convert` milestone plan, `covers: [R1, R2, R4, R5, R1000, R1001]` — chosen: the formatting rule has no observable surface until the CLI prints something, so folding it in is the only shape that yields a vertical slice, and the plan then goes through the normal `docs/plans/` path with the owner's `CODEOWNERS` review rather than the unattended `docs/plans/oracle/` path — strictly more oversight, not less. (b) A standalone steward plan under `docs/plans/oracle/` covering R1000 alone — rejected: BL-5 records exactly why it cannot be written — it would deliver a formatting function with no printed output to govern, would have to invent or borrow the invocation syntax to write the `acceptance/S1.sh` row OD-1 requires, and would re-touch every file the `convert` plan touches a night later. (c) A steward plan covering R1000 plus the syntax and the error paths needed to exercise it — rejected: that is the `convert` milestone under another name, cut on the unattended path for no gain. (d) Leave the choice to the steward — rejected: BL-5 is a HIGH-risk filed uncertainty, so planning is stopped until a decision cites it; not choosing is the one option the process has already ruled out.
- **Rationale:** BL-5's first half asks which plan carries R1000, and its proposed default — fold into `convert`, cut no steward plan — is also what `docs/oracle/handoff-2026-08-20-1.md` recommended and what `AGENTS.md`'s vertical-slice rule implies: a plan must deliver something observable end-to-end, and a 12-significant-digit rule is observable only through a command that prints. OD-1's phrase "the plan that implements R1000" now resolves to the milestone `convert` plan (slug `convert`, at `docs/plans/convert.md`), which carries everything OD-1 named: the ESC-1 reproducer as a row in `acceptance/S1.sh` (0.1 km to m prints exactly `100`), unit tests asserting the formatting rule at representative magnitudes, and — after both merge — ESC-1's completing correction row in `docs/escapes.md`. No new measurement is needed for this decision itself: which plan covers R1000 is exactly what `.github/scripts/coverage.sh` and the `plan` check already observe.

## OD-5 — One-shot invocation is `anvil <value> <from-unit> <to-unit>`, printing the converted value alone on stdout

- **Date:** 2026-08-20
- **Evidence:** BL-5
- **Requirements added:** R1001
- **Requirements superseded:** (none)
- **Vision statement relied on:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently." It could be read to favour a self-describing flag syntax (`--from`, `--to`) on the ground that named arguments make mistakes harder to make and errors easier to explain. It does not forbid this ruling: V2 governs how errors behave, not how arguments are spelled, and the error contract is already fixed by R4 and R5 — a wrong unit, a swapped pair, or a bad arity refuses loudly under either syntax. Routing diagnostics to stderr (below) serves V2 directly: an error can never masquerade as a result in a pipe.
- **Alternatives considered:** (a) `anvil <value> <from-unit> <to-unit>`, value alone on stdout — chosen: it is BL-5's own proposal, it reads in the order the request is spoken ("convert 0.1 km to m"), it mirrors the converter's signature `(value, from-unit, to-unit)`, and three mandatory positionals are the smallest possible surface. (b) `anvil <from-unit> <to-unit> <value>` — rejected: no advantage, and it breaks the spoken order §4's use cases are written in. (c) A filler-word form, `anvil 0.1 km to m` — rejected: a fourth token that carries no information, one more arity case for R5 to police, and a unit named `to` becomes unparseable; complexity with no correctness gain is what V3 rules out. (d) Flags, `anvil --from km --to m 0.1` — rejected: flags earn their keep when arguments are optional, and none are; for §4's terminal user it is strictly more typing for the same behaviour. (e) A subcommand form, `anvil convert ...` — rejected: a namespace for one verb serves a breadth §3's non-goals already renounce. (f) Decorated output, `0.1 km = 100 m` — rejected: §4's script author wants the number; decoration on stdout forces every script to parse it back out, and S1's "prints exactly `100`" measurement is only writable against a bare value.
- **Rationale:** BL-5's second half records that `acceptance/S1.sh` cannot be written while the syntax is unruled: S1 measures the installed `anvil` command, `docs/DESIGN.md` §11 deliberately leaves the syntax undecided, and the design's test note routes exactly this question here rather than to the planning layer. The proposed default would have the `convert` planner re-file the syntax as its own uncertainty — but that question is already before the oracle, classified HIGH, with a concrete proposal attached; sending it back to be re-filed spends a full planning round deciding nothing, and a decision deferred costs a night. So it is ruled now, as BL-5's standalone-plan arm proposed it. No new measurement mechanism is needed: `acceptance/S1.sh` and `acceptance/S3.sh` invoke the installed command in exactly this syntax on every pull request, so every row in them is a standing measurement of R1001, and the unit tests the `convert` plan carries cover the stream separation.

**R1001** — One-shot invocation syntax: `anvil <value> <from-unit> <to-unit>` —
exactly three positional arguments, no subcommand, no flags required. On
success the converted value is printed alone on standard output, as a single
line formatted per R1000, and the exit code is zero. The diagnostics R4 and R5
require are printed to standard error, never standard output, so an error line
cannot be mistaken for a result by a consuming script. This fixes the one-shot
form only: how batch mode is invoked and what its line format looks like remain
the open questions `docs/DESIGN.md` §11 records, to be filed by the
`convert-batch` planning round. *Evidenced by:* S1, S3.
