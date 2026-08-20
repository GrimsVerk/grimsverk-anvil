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

## OD-1 — Results print at 12 significant digits, trailing zeros stripped

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V3 — "Simplicity comes before completeness: a
  small tool that is obviously right beats a large one that must be trusted."
  A rounding rule is added machinery, but it is one format specification
  applied at the single point where a result is printed; shipping raw float
  noise would make the tool *less* obviously right, so the statement does not
  forbid this — it argues for the smallest rule that removes the artifact,
  which is what was chosen.
- **Alternatives considered:** (a) print the raw float `repr` — rejected: that
  is exactly what produced ESC-1's `100.00000000000001`, an artifact presented
  as a result; (b) a fixed count of decimal places — rejected: the tool spans
  magnitudes (mg→kg is 1e-6), so any fixed count either pads integer results
  with noise zeros or truncates small results to nothing; (c) `decimal.Decimal`
  arithmetic throughout — rejected: temperatures are affine functions and the
  whole factor table would need re-expressing; real machinery to suppress noise
  that sits far below any physical measurement, against V3; (d) 15 or more
  significant digits — rejected: a double carries ~17, and error accumulated
  through the base-unit hop can reach past the 15th digit, so artifacts could
  still surface; 12 leaves margin below the noise floor while remaining far
  more precision than any practical conversion needs.
- **Rationale:** ESC-1 is the failure V1 names, observed by hand before the
  first run: a floating-point artifact printed as if it were the answer, and a
  design (§11, deliberately) silent on whether that is a defect. It is a
  defect. 0.1 km is exactly 100 m; a tool whose correctness is its first
  priority must not print `100.00000000000001` for it. Rounding to 12
  significant digits collapses one-ulp noise from the base-unit hub to the
  mathematically exact value in every case the unit table can produce, while
  leaving every meaningful digit of every real conversion intact. Confidence
  is high on the rule's intent and moderate on the digit count — if 12 proves
  wrong in either direction, a superseding decision costs one entry.

**R1000 — Output precision.** A printed result value is formatted to at most
12 significant digits with trailing zeros stripped — Python
`format(value, ".12g")` semantics, including `%g`'s switch to scientific
notation at extreme magnitudes — in single-shot and batch output alike.
Error and usage messages are prose, not results, and are untouched by this
rule. *Evidenced by:* S1, whose fixed table must include ESC-1's own case:
`0.1 km` to `m` prints exactly `100`.

**Measurement.** This decision changes printed output, and the existing
mechanism that observes printed output is the §13 acceptance scripts, run on
every pull request. `acceptance/S1.sh` asserts exact expected strings, so the
rule is observed there once its table carries the ESC-1 case above — which is
also precisely the script ESC-1's check column left pending ("whatever
precision rule the design layer settles, expressed as an acceptance script").
The plan that implements R1000 carries that table row; once it has merged,
ESC-1 takes its correction row in `docs/escapes.md` naming the demonstrated
check. Per the vision's durable-evidence section: "A change nothing can
observe is a change nobody can evaluate."

Downstream: R1000 belongs to the MVP `convert` milestone's print layer; no
plan exists yet, so it is new-plan work, not a change to a landed one. The
other §11 gaps (CLI syntax, batch line format) have no logged evidence yet and
are deliberately not ruled on here.

## OD-2 — HALTED: BL-3's aligned, colored tables via the `rich` library

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Tenet relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet."
- **What a decision would have said:** grant BL-3 as filed — add `rich` as a
  runtime dependency and print results as aligned, colored tables. BL-3 asks
  for `rich` *specifically* and calls hand-rolled ANSI codes wasted effort, so
  the stdlib route the tenet permits is exactly what the item rules out; there
  is no reading of BL-3 that both satisfies it and keeps V5. The oracle also
  does not simply reject it: BL-3 is owner-filed and V5 is owner-written, and
  adjudicating one owner artifact against another is not steering the oracle
  can do from the vision — it is the vision in conflict with its own author,
  which is the one case this ledger records instead of deciding.
- **What it needs from the owner:** one sentence, either way. Edit V5 to carve
  out what BL-3 needs (for example, a named exception for display-only
  dependencies), and BL-3 becomes plannable as filed. Or withdraw the `rich`
  requirement by filing a successor to BL-3, and the remaining question —
  plain output versus hand-rolled alignment — becomes decidable under V3.
  Until one happens, nothing plans or builds BL-3.

## OD-3 — Currency conversion (BL-4) is rejected; the offline non-goal stands

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted." Also V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** (none — no statement in docs/VISION.md tells
  against this). The vision was read whole looking for one: BL-4's own
  argument is completeness — "a converter that cannot do money feels
  half-finished" — and completeness is exactly what V3 ranks below
  simplicity; V4 goes further and calls breadth expendable. Nothing in the
  file argues the other way.
- **Alternatives considered:** (a) grant BL-4 as filed, with live rates
  fetched at run time over stdlib `urllib` — rejected: it deletes the design's
  offline/deterministic requirement (R8) and its §3 non-goal, adds a network
  failure mode to every invocation, and makes the test suite's offline rule
  unable to cover the feature; a large trust surface bought for breadth, the
  trade V3 forbids. (b) currency with fixed, compiled-in rates — rejected:
  unlike metres per mile, an exchange rate decays, so a compiled-in rate is a
  wrong number presented confidently within days of shipping — the V1 worst
  case wearing a feature's clothes. (c) defer for a future run — rejected:
  a pending decision is the failure this role exists to prevent; if the owner
  wants currency they can re-file with the vision amended, and a superseding
  decision costs one entry.
- **Rationale:** BL-4 contradicts the design twice over — §3 names "currency,
  time zones, or any unit that needs live data" a non-goal, and R8 requires
  fully offline and deterministic operation — and the vision backs the design
  on both counts, so the design stands and the item is rejected rather than
  metabolised. No requirement changes. A currency symbol given to `anvil`
  today is an unknown unit, and R4 already requires the loud, named error
  that V2 wants for it. Nothing about this decision changes behaviour, so
  there is nothing new to measure: the existing R4/S3 error path is the
  observable surface, and it is already gated on every pull request.
  Confidence is high — this is the vision agreeing with the design against a
  single-sentence proposal.

## OD-4 — BL-5 is granted: `od1-output-precision` covers R1000 while delivering the single-shot half

- **Date:** 2026-08-20
- **Evidence:** BL-5
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** (no vision statement decided this)
- **Vision statements against:** V6 — "A conversion that is numerically wrong,
  however plausible it looks, is rejected outright — as is any run that reports
  success while a criterion's evidence cell is empty or narrated rather than
  executed." This is the nearest statement, because letting a plan claim
  `covers: [R1000]` while batch mode is unbuilt looks like reporting a whole
  where only a half exists. It does not forbid the ruling: `covers:` feeds
  `coverage.sh`, which answers "is every requirement *planned*" and nothing
  more — `docs/acceptance.md` says in its own words that even a full coverage
  pass "only means the work was scheduled, not that it works". Doneness is
  claimed by acceptance evidence, not by coverage, and no acceptance row is
  touched by this ruling. Nothing here lets a run report success on an empty
  evidence cell.
- **Alternatives considered:** (a) rule no and split the requirement —
  supersede R1000 with a single-shot requirement and a separate batch
  requirement, so `coverage.sh` mechanically forces the future `convert-batch`
  plan to claim the batch half. Rejected: it spends two new requirement ids
  and a frontmatter change to an already-merged plan to buy enforcement the
  acceptance layer already provides more directly — a printed-output rule is
  observed by acceptance scripts run on every pull request, not by coverage
  bookkeeping, and the batch half gets exactly that observation via the
  obligation recorded below. (b) rule no and hold the plan until batch exists,
  so one plan delivers both halves at once. Rejected: it inverts the build
  order the plan correctly derived (conversions first, precision at the print
  point second), and it leaves ESC-1 open for an entire unbuilt milestone for
  no behavioural gain — every candidate answer produces the same code and the
  same printed output, so waiting buys nothing observable. (c) the filed
  default: yes, the plan covers R1000 and delivers the single-shot half —
  accepted.
- **Rationale:** The steward's risk classification was correct: every candidate
  answer leaves the same code, the same slice boundaries, the same signature
  and the same printed output, so this is coverage bookkeeping, not design.
  The plan makes `format_result` the only point where a result value becomes
  text, which is precisely the shape OD-1 chose ("one format specification
  applied at the single point where a result is printed"), and it is what
  makes the coverage claim honest rather than optimistic: the batch milestone
  cannot print a result except through the function that already carries the
  rule, unless it deliberately routes around it. That residual risk is handled
  by obligation, recorded here so the batch planner derives it instead of
  guessing: the `convert-batch` plan (R6) must (1) print its result lines
  through `format_result`, and (2) carry a precision-sensitive row in
  `acceptance/S5.sh`'s batch fixture — the ESC-1 case as a batch line, whose
  result field prints exactly `100` — so the batch half of R1000 is observed
  by the same mechanism OD-1 named for the single-shot half. This ruling
  itself changes no behaviour, so there is nothing new to measure now; the
  batch-half measurement lands with the batch plan, and it is an existing §13
  script pointed at a new row, not new machinery. Confidence is high.

Downstream: `docs/plans/oracle/od1-output-precision.md` proceeds exactly as
landed — no frontmatter change, no new requirement, nothing re-planned. BL-5
leaves the uncertainty queue by this citation. The two obligations above bind
the future `convert-batch` plan and are restated in this run's handoff.

## OD-5 — Invocation syntax: `anvil <value> <from-unit> <to-unit>`; batch via `--batch`; a bare `anvil` is a usage error

- **Date:** 2026-08-20
- **Evidence:** BL-6
- **Requirements added:** R1001
- **Requirements superseded:** (none)
- **Vision statement relied on:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently." Also V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** V3 — "Simplicity comes before completeness: a
  small tool that is obviously right beats a large one that must be trusted."
  It is the nearest, because the zero-flag alternative exists: detect a
  non-tty standard input and enter batch mode implicitly, and then `--batch`
  is added machinery. It does not forbid the flag: implicit detection is
  hidden behaviour — the same command line does different things depending on
  how it was launched, which is a tool that "must be trusted" rather than one
  that is obviously right — and it makes a bare `anvil` at a terminal block
  silently waiting for input instead of refusing loudly, which is exactly what
  V2 forbids. One explicit, visible flag is the smaller trust surface, so V3
  argues for it, not against it.
- **Alternatives considered:** (a) a subcommand form, `anvil convert 5 km mi` —
  rejected: the tool does one thing, so the subcommand token buys extensibility
  nobody asked for at the price of four tokens where three carry the meaning,
  against V3; (b) a filler word, `anvil 5 km to mi` — rejected: a fourth token
  to parse, misspell, and report usage errors about, with no information in it;
  (c) batch entered implicitly when arguments are absent or stdin is not a tty
  — rejected: a bare `anvil` at a terminal would hang silently instead of
  printing usage, which both R5 and V2 rule out, and behaviour that depends on
  how the process was launched is guessing silently; (d) batch as a
  subcommand, `anvil batch` — rejected: it mixes two grammars (subcommand for
  batch, positionals for single-shot) where one flag keeps one grammar; (e)
  the filed default — three positionals in the order value, from-unit,
  to-unit; `--batch` reading standard input; exact §5 symbols — accepted.
- **Rationale:** BL-6 is the HIGH uncertainty the design left open on purpose
  (§8, §11), and every candidate syntax is buildable, so the vision's
  tiebreakers choose: the smallest grammar whose refusals are loud. The
  positional order value, from-unit, to-unit reads as the request is spoken —
  "5 km in miles" — and matches §1's own phrasing ("you give it a value, the
  unit it is in, and the unit you want"). Making a bare `anvil` a usage error
  rather than a stdin read keeps R5 simple and honest now, and reserving
  `--batch` decides today's behaviour without building R6. Unit symbols match
  §5 exactly because BL-1 (aliases) is unruled — a ruling there supersedes
  that one sentence and nothing else here. Confidence is high on the shape
  (positionals, explicit flag, loud bare-invocation error) and moderate on
  cosmetics like the flag's spelling; a superseding decision costs one entry.

**R1001 — Invocation syntax.** Single-shot: exactly three positional
arguments, in the order value, from-unit, to-unit — `anvil 5 km mi` — with no
subcommand. Batch (R6): `anvil --batch` reads requests from standard input and
accepts no positional arguments. Every other invocation — a bare `anvil`, a
wrong positional count, `--batch` combined with positionals, an unrecognised
flag — is a usage error under R5: usage text and a non-zero exit. Unit symbols
are matched exactly as `docs/DESIGN.md` §5 spells them, case-sensitively; if
BL-1 is later granted, its decision supersedes this matching sentence only.
Until the `convert-batch` milestone builds R6, `--batch` is reserved, not
delivered: the MVP treats it as an unrecognised flag, a usage error under R5.
*Evidenced by:* S1 and S3, whose command lines this requirement fixes; S5
exercises `--batch` once R6 exists.

**Measurement.** This decision fixes the exact command lines the §13 scripts
execute. The existing mechanism — `acceptance/S1.sh` and `acceptance/S3.sh`,
run as a required check on every pull request — is the observation: S1's table
invokes `anvil <value> <from> <to>` literally, and S3 must include the bare
`anvil` invocation among its missing-argument cases. Both scripts are written
by the `convert` milestone plan, which until this decision could not write
them. No new mechanism is needed; per the vision's durable-evidence section,
the scripts that observe the interface are the ones this ruling unblocks.

Downstream: R1001 belongs to the MVP `convert` milestone's CLI layer. No plan
exists for that milestone yet — BL-6 was filed precisely because planning
stopped on it — so this is new-plan work, and the plan claims R1001 in its
`covers:` list.

## OD-6 — Single-shot output: the formatted value alone on standard output; errors and usage on standard error

- **Date:** 2026-08-20
- **Evidence:** BL-7
- **Requirements added:** R1002
- **Requirements superseded:** (none)
- **Vision statement relied on:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** V2 — "Clear, honest errors come before
  feature breadth: refusing loudly beats guessing silently." It is the
  nearest, because a bare `100` names no unit, so a misread invocation yields
  a plausible number with no context on the line to catch it — which sounds
  like the silence V2 distrusts. It does not forbid this: V2 is about errors,
  and under this contract every error is loud — named offending input on
  standard error, non-zero exit, nothing on standard output to mistake for a
  result. A successful result is not a guess: both units were fixed by the
  command line the caller typed one moment earlier, and echoing their own
  question back at them is output breadth, not error clarity. The §4
  script-author, a named user, would have to strip that echo from every pipe.
- **Alternatives considered:** (a) echo the request on the result line —
  `5 km = 3.10685596119 mi` — rejected: friendlier to eyes, but every script
  consumer must parse the value back out of prose, and `docs/DESIGN.md` §4
  names the script author piping a thousand rows as a core user; decoration
  that taxes the primary consumer, against V3; (b) the value with a target-unit
  suffix, `3.10685596119 mi` — rejected: the same parsing tax, smaller; the
  target unit is the third argument the caller chose and adds no information;
  (c) errors on standard output — rejected: a pipe would ingest error prose as
  data, a wrong "number" delivered confidently downstream, the V1/V6 worst
  case; standard error plus a non-zero exit is the loud refusal V2 requires
  and R4/R5 already demand the exit code; (d) the filed default — the
  formatted value alone on standard output, one line, errors and usage on
  standard error — accepted.
- **Rationale:** R1000 (OD-1) fixed how a result value is formatted; BL-7
  asks what else shares its line and which stream carries what. The answer
  that is obviously right is: nothing else, and standard output carries
  results only. It makes the tool composable the way §4 promises — `anvil` in
  a pipe emits exactly the number — and it retroactively makes
  `od1-output-precision`'s asserted string honest: the "printed value field"
  is the whole line, so the ESC-1 case prints exactly `100` and a script can
  assert it with `=`, not a regex. This is an external format, expensive to
  reverse once scripts parse it, which is why it is decided now, before
  `acceptance/S1.sh` and `acceptance/S3.sh` exist, rather than shipped by
  accident and defended later. Confidence is high.

**R1002 — Single-shot output contract.** On success, `anvil` writes exactly
one line to standard output: the result value formatted per R1000, with no
unit suffix, no echo of the input, and no other text — the line is
`format(value, ".12g")` of the result, then a newline, and nothing else is
ever written to standard output. Error and usage messages (R4, R5) are written
to standard error, and a failed invocation writes nothing to standard output.
This requirement governs single-shot output only; the batch line format (R6)
remains undecided in `docs/DESIGN.md` §11 and is not ruled here. *Evidenced
by:* S1, whose expected values are compared against the whole output line, and
S3, which must additionally assert that error and usage text arrive on
standard error while standard output stays empty.

**Measurement.** The behaviour this decision fixes is printed output and
stream separation, and the existing mechanism that observes printed output is
the §13 acceptance scripts on every pull request. Two obligations on the
`convert` plan make the contract observed rather than narrated:
`acceptance/S1.sh` compares the entire stdout line (not a substring) against
each expected value, and `acceptance/S3.sh` asserts stderr carries the message
and stdout is empty for each failure case. Existing machinery, pointed at the
new contract; nothing new is invented, per the vision's durable-evidence
section.

Downstream: R1002 belongs to the MVP `convert` milestone's CLI layer,
alongside R1001; the same new plan claims it. `docs/plans/oracle/od1-output-precision.md`
is untouched — its slice 1 already prints through one function and its
asserted string is now exact rather than presumed.

## OD-7 — BL-8 is granted: the `convert` plan covers R7 and R8

- **Date:** 2026-08-20
- **Evidence:** BL-8
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** (no vision statement decided this)
- **Vision statements against:** V6 — "A conversion that is numerically wrong,
  however plausible it looks, is rejected outright — as is any run that
  reports success while a criterion's evidence cell is empty or narrated
  rather than executed." It is the nearest, because letting the `convert`
  plan claim R7 and R8 looks like claiming the packaging and the stdlib-only
  posture are delivered by bookkeeping. It does not forbid the ruling, for the
  reason OD-4 already recorded: `covers:` feeds `coverage.sh`, which answers
  "is every requirement planned" and nothing more. Doneness for R7 and R8 is
  S4 — an **(owner)** criterion, verified by the owner on their own machine —
  and no acceptance row is touched by this ruling; its evidence cell stays
  empty until the owner fills it.
- **Alternatives considered:** (a) a separate packaging plan for R7 and R8 —
  rejected: it would contain no work of its own, because the installed `anvil`
  console command and the dependency-free posture come into existence in
  exactly the MVP's diff (the scaffolded `pyproject.toml` entry point and the
  absence of any added dependency); a plan that is frontmatter around another
  plan's work is bookkeeping pretending to be a slice; (b) leave R7 and R8
  uncovered until a later milestone — rejected: §12's later milestones
  (`temperature`, `convert-batch`) do not create the package or the dependency
  posture either, so `coverage.sh` would report two requirements nobody ever
  scheduled, permanently, for work the MVP in fact does; (c) route through an
  edit to `docs/DESIGN.md` §12's scope line — not available to this ledger
  (that document is owner-landed) and unnecessary, since §12 scopes the MVP by
  its acceptance criteria and R7/R8's criterion S4 is the owner's own run, not
  a per-PR gate; (d) the filed default: yes, `covers: [R1, R2, R4, R5, R7,
  R8]` — accepted.
- **Rationale:** The same shape as BL-5/OD-4, and the planner's LOW
  classification was correct: no slice boundary, signature, external format or
  printed output changes on any candidate answer — only the coverage
  bookkeeping differs, and reversing it costs one line of plan frontmatter.
  The milestone that first makes R7 and R8 true is the one that should carry
  their ids, so that `coverage.sh`'s "covered" means "scheduled where the work
  actually happens". This ruling changes no behaviour, so there is nothing new
  to measure: R7 and R8's observable surface is S4, already assigned to the
  owner by §13, plus the offline test-suite rule CI enforces on every pull
  request. The `convert` plan should claim R1001 and R1002 in the same
  `covers:` list — they landed in this run and live in the same milestone.
  Confidence is high.

## OD-8 — BL-9 is granted: a non-finite parse (`nan`, `inf`, overflow) is an R4 error

- **Date:** 2026-08-20
- **Evidence:** BL-9
- **Requirements added:** R1003
- **Requirements superseded:** (none)
- **Vision statement relied on:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently." Also V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V3 — "Simplicity comes before completeness: a
  small tool that is obviously right beats a large one that must be trusted."
  It is the nearest, because the zero-guard implementation exists: accept
  whatever `float()` accepts, add nothing. It does not forbid the guard: a tool
  that prints `nan` as a result line is precisely one that "must be trusted"
  rather than being obviously right, since the meaningless answer is
  number-shaped and flows silently down a pipe; and the guard is one finiteness
  check inside the function that already raises this exact error. V3 argues for
  the smallest rule that keeps every printed result meaningful, which is what
  was chosen.
- **Alternatives considered:** (a) let them convert — `anvil nan km mi` prints
  `nan`, `anvil 1e400 km mi` prints `inf` — rejected: a number-shaped answer
  that means nothing, presented confidently on standard output where R1002
  promises a result; a script consumer ingests it as data, which is the V1/V6
  worst case, and `nan` additionally propagates through downstream arithmetic
  without ever failing, the exact opposite of V2's loud refusal. (b) blacklist
  the literal spellings before parsing — rejected: `float()` accepts many
  spellings (`nan`, `NaN`, `Infinity`, `INF`, with signs and surrounding
  whitespace), so a string list chases an open set, and it cannot catch `1e400`
  at all, which is digit-shaped and only becomes infinite after parsing;
  checking the parsed value for finiteness catches every route to a non-finite
  result in one guard. (c) reject `nan` but admit infinities — rejected: an
  infinite length is exactly as meaningless a conversion result as `nan`, and
  admitting it re-opens the overflow route the evidence names. (d) the filed
  default — parse, then reject any non-finite result with the same named error
  raised for `five` — accepted.
- **Rationale:** The steward's LOW classification was correct — one guard
  inside `parse_value`, no signature, slice boundary, external format or
  existing S1/S3 case changes on either answer — but the behaviour it decides
  is external: whether `anvil nan km mi` refuses or answers. R4 already makes
  "a value that is not a number" a named error, and `nan` and `inf` are the
  IEEE spellings of "no meaningful number here"; a design whose §6 assumes
  integer and decimal inputs did not intend `float()`'s full grammar to widen
  what counts as an answer. The ruling is deliberately expressed as a
  finiteness condition on the parsed value, not as a list of spellings, so it
  is robust to the §6 question it does not decide: whether scientific notation
  like `1e5` is accepted stays open ("may be ignored"), and R1003 holds on
  either answer — if the parser accepts scientific notation, finite values pass
  and overflowing ones refuse; if it rejects it wholesale, `1e400` is already a
  parse error. Confidence is high.

**R1003 — Non-finite values are not numbers.** A value token whose parse does
not yield a finite float is "a value that is not a number" under R4. This
covers `nan`, `inf` and `-inf` in every spelling `float()` accepts, and any
literal whose value overflows to infinity, such as `1e400`. The refusal is
R4's, unchanged: an error message naming the offending token on standard
error, a non-zero exit, and nothing on standard output (R1002). Equivalently:
the value parser returns only finite floats. *Evidenced by:* S3, whose cases
must include at least one non-finite spelling and one overflowing literal.

**Measurement.** This decision changes a CLI refusal, and the existing
mechanism that observes refusals is `acceptance/S3.sh`, run on every pull
request. The landed `convert` plan (`docs/plans/oracle/od5-convert-cli.md`)
already carries the guard itself — its slice 1 contract has `parse_value`
raising `NotANumberError` on a non-finite result, naming it the BL-9 default,
with unit tests — but its S3 script fixes seven cases and none is non-finite,
so as planned the guard is observed by unit tests only, not by the §13 layer
that outlives any one plan. The plan that claims R1003 therefore adds two rows
to `acceptance/S3.sh`: `anvil nan km mi` asserting standard error names
`nan`, and `anvil 1e400 km mi` asserting standard error names `1e400` — each
with a non-zero exit and empty standard output, the same assertions the
script's existing cases make. Existing machinery pointed at new rows, per the
vision's durable-evidence section; nothing new is invented.

Downstream: the `convert` plan proceeds exactly as landed — the guard is
already in its slice 1 contract and no slice changes. R1003 is new-plan work
of the smallest kind: the two S3 rows above, buildable only once the
`convert` milestone has produced `acceptance/S3.sh`, in the same after-the-MVP
position `od1-output-precision` occupies. BL-9 leaves the uncertainty queue by
this citation.

## OD-9 — Batch request line: three whitespace-separated tokens in R1001's order; blank lines are skipped

- **Date:** 2026-08-20
- **Evidence:** BL-10
- **Requirements added:** R1004
- **Requirements superseded:** (none)
- **Vision statement relied on:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** V2 — "Clear, honest errors come before
  feature breadth: refusing loudly beats guessing silently." It is the
  nearest, because skipping an empty line silently can be read as the silence
  V2 forbids. It does not forbid it: a skip produces no answer and fabricates
  nothing, so nothing is guessed — V2's target is a wrong or missing refusal,
  and a blank line makes no request to refuse. Treating blank lines as
  failures would turn the grouping whitespace and trailing blank lines
  ordinary human-edited files carry into refusals about nothing, and error
  noise a consumer learns to ignore is the opposite of the loud refusal V2
  wants. Every line that carries any token and is not a well-formed request
  is refused loudly, per R6.
- **Alternatives considered:** (a) comma-separated fields, `5,km,mi` —
  rejected: a second grammar (quoting, embedded separators) for fields that
  can never contain the separator, and the batch line stops matching the
  command line for no gain; machinery against V3. (b) full command lines per
  row, with flag parsing — rejected: a request line is data, not a program
  invocation; importing the R5/R1001 flag grammar into a data format adds
  parse states nobody asked for. (c) a comment syntax and/or a header row —
  rejected: no logged evidence asks for either, a generated thousand-row file
  needs neither, and V4 calls that breadth expendable. (d) a blank line as a
  failed line — rejected for the reason weighed in the field above: it
  refuses loudly about nothing. (e) the filed default — three
  whitespace-separated tokens in R1001's positional order, surrounding
  whitespace ignored, blank or whitespace-only lines skipped, any other token
  count a failed line — accepted.
- **Rationale:** BL-10 is the first half of the format `docs/DESIGN.md` §11
  deliberately left open, and every candidate is buildable, so the tiebreaker
  chooses the grammar that is already fixed elsewhere: R1001 (OD-5) fixed the
  order value, from-unit, to-unit for the command line, and a request line
  that is exactly those three tokens makes the whole format one sentence and
  the reader a whitespace split. A user who knows the tool already knows the
  file format. Unit symbols match exactly as R1001 requires, and its BL-1
  caveat carries over unchanged. No flag parsing applies inside a line —
  tokens are data, so `-5 km mi` is a request, not an option. Confidence is
  high on the token form and the failed-line rule, moderate on skipping blank
  lines silently; if the owner would rather see blank lines refused, a
  superseding decision costs one entry.

**R1004 — Batch request line format.** In batch mode (R6), each line of
standard input is a conversion request: exactly three whitespace-separated
tokens, in R1001's positional order — value, from-unit, to-unit — so
`5 km mi`, with leading and trailing whitespace ignored. Unit symbols are
matched exactly as R1001 fixes them, case-sensitively; a BL-1 ruling that
supersedes R1001's matching sentence supersedes this one identically. There
is no comment syntax, no header row, and no separator other than whitespace,
and no flag parsing applies inside a request line. An empty or
whitespace-only line is skipped: it produces no output line and does not
affect the exit code. Any other line that does not split into exactly three
tokens is a failed line under R6. *Evidenced by:* S5, whose fixture is
written in this format, and which also asserts the blank-line skip (see
Measurement).

**Measurement.** This decision fixes an external input format, and the
existing mechanism that observes external formats is the §13 acceptance
scripts, run on every pull request. `acceptance/S5.sh` does not exist yet —
BL-10 was filed precisely because it could not be written — so the
`convert-batch` plan that implements R1004 writes it, with the five-line
fixture in this format. One behaviour here sits outside S5's five-line
criterion: the blank-line skip. The same script therefore also runs a second
standard-input document — two valid requests separated by a blank line —
asserting exactly two output lines and exit code 0. Existing machinery
pointed at a new case, per the vision's durable-evidence section; nothing new
is invented.

Downstream: R1004 belongs to the `convert-batch` milestone (R6). No plan for
it exists yet — this ruling and OD-10 are what unblock the planner — so this
is new-plan work, not a change to a landed plan. BL-10 leaves the uncertainty
queue by this citation.

## OD-10 — Batch output: one stdout line per request, in input order; a failed line prints `error: <message>` in place; stderr stays empty

- **Date:** 2026-08-20
- **Evidence:** BL-11
- **Requirements added:** R1005
- **Requirements superseded:** (none)
- **Vision statement relied on:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently." Also V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V1 — "Correct conversions come before
  everything else: a wrong number presented confidently is the worst output
  this tool can produce." It is the nearest, because OD-6 rejected
  errors-on-stdout for single-shot exactly on this ground: a pipe ingests
  error prose as data. It does not forbid this: an `error:` line is not
  number-shaped — an R1000 result is `%g` output, digits, sign, point,
  exponent, never the string `error:` — so a consumer that parses it as a
  number fails loudly at parse time, and one that checks the prefix gets the
  exact failing row. The stderr alternative is the one that produces V1's
  failure here: with fewer stdout lines than input lines, every row after the
  first failure is a right-looking number silently attached to the wrong
  question — wrong numbers presented confidently, at scale, with no in-band
  marker to catch them. In batch, in-band errors are the loud option.
- **Alternatives considered:** (a) errors on standard error, results only on
  standard output — the property OD-6 chose for single-shot — rejected:
  single-shot has one request per exit code, so the caller always knows what
  failed; a batch run has one exit code for a thousand rows, and losing the
  row-to-row correspondence turns a partial failure into silent misalignment,
  the V1 worst case weighed above. Recovering correspondence by numbering
  stderr lines is new machinery against V3. (b) result lines that echo the
  request — rejected: OD-6 already rejected the echo for single-shot, OD-4
  obliges batch results through `format_result` identical to the single-shot
  line, and the parsing tax lands on §4's script author, the format's primary
  consumer. (c) a sentinel on the failed row — an empty line, `-`, or `NaN` —
  with details on standard error — rejected: it keeps alignment but the
  sentinel is either number-shaped (`NaN`, exactly the meaningless
  number-shaped answer R1003 just banned) or invisible, and it splits one
  failure across two streams; the error text belongs where the row is.
  (d) exit code alone, no per-row marker — rejected: R6 already requires an
  error line, and discarding which row failed makes a thousand-row failure a
  needle hunt, against V2. (e) the filed default — one stdout line per
  non-skipped request in input order, success identical to the single-shot
  line, failure as `error: <message>` in place, stderr empty, exit non-zero
  if any line failed — accepted.
- **Rationale:** BL-11 is the second half of the §11 gap, and the planner was
  right that the two candidates genuinely pull against each other; the vision
  decides it through what each does to the consumer. The chosen contract
  keeps line N of the output answering line N of the input, which is the
  property that makes batch worth using from a script, and it makes every
  failure loud in the one place the consumer is already looking — the row —
  prefixed with a marker no result can ever be and carrying the same
  offending-input message (R4, R1003) single-shot prints. R1002 is untouched:
  it governs single-shot only, by its own text, and OD-6's reasoning is
  re-weighed here rather than overruled — the stream split that protects a
  single-shot pipe is the thing that corrupts a batch one. Confidence is high
  on the shape (in-band, in-order, one line per request); the exact prefix
  spelling is cosmetic and a superseding decision costs one entry.

**R1005 — Batch output contract.** In batch mode (R6), standard output
carries exactly one line per non-skipped request line (R1004), in input
order. For a successful request the line is the result value formatted per
R1000, identical to the single-shot line R1002 fixes: no unit suffix, no echo
of the request, nothing else. For a failed line it is `error: ` — lowercase,
colon, one space — followed by the same message single-shot writes to
standard error for that failure, which names the offending input (R4, R1003);
a line with the wrong token count (R1004) is a failed line with a message
naming that line's defect. Nothing else is ever written to standard output,
and standard error stays empty for the whole batch run. The exit code is
non-zero if any line failed and 0 otherwise, including an input with no
requests. A defective invocation itself — `--batch` with positionals, an
unknown flag — is not batch output; it is a usage error under R5 and R1001
and follows R1002's streams. *Evidenced by:* S5, whose expected output is
compared whole-line against this contract.

**Measurement.** This decision fixes an external output format, and the
existing mechanism that observes printed output is the §13 acceptance scripts
on every pull request. `acceptance/S5.sh` — written by the `convert-batch`
plan, which until this decision could not write it — asserts the exact
expected standard-output lines, whole-line as OD-6 obliged for S1, including
the `error:` line at its fixture position; asserts standard error is empty;
and asserts the non-zero exit. Its fixture carries OD-4's obligation: the
ESC-1 precision row, `0.1 km m`, whose output line is exactly `100`. Existing
machinery pointed at the new contract, per the vision's durable-evidence
section; nothing new is invented.

Downstream: R1005 belongs to the `convert-batch` milestone (R6), alongside
R1004; the same new plan claims both. With OD-9 that milestone's three
inherited obligations from OD-4 and OD-5 now have their missing halves, and
planning is unblocked. `docs/plans/oracle/od5-convert-cli.md` is untouched —
R1001's "`--batch` is reserved" sentence already anticipates R6 being built
later. BL-11 leaves the uncertainty queue by this citation.
