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

## OD-1 — Results print with at most 12 significant digits, via Python's `.12g` format

- **Date:** 2026-08-20
- **Evidence:** ESC-1
- **Requirements added:** R1000
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V6 — "A conversion that is numerically wrong, however plausible it looks, is rejected outright" (first clause) — rounding discards digits, which could be read as printing a number different from the computed one. It does not forbid this: the discarded digits are binary floating-point representation noise (a double is reliable to roughly 15–17 significant decimal digits, and the ESC-1 artifact lives exactly there), so printing them is the numerically-wrong output and removing them is what the statement demands.
- **Alternatives considered:** (1) shortest-round-trip `repr` — that is precisely what produced `100.00000000000001`, the artifact ESC-1 logs; (2) a fixed count of decimal places — magnitude-dependent, so it truncates small results (mm to km) toward zero and pads large ones with useless zeros; (3) `.15g` or `.17g` — still admits representation artifacts, which begin around the 16th significant digit; (4) fewer digits such as `.6g` — discards real precision a scripted consumer of batch mode (R6) may rely on, trading correctness for looks.
- **Rationale:** The escape is exactly V1's case: the mathematics said 100 and the binary representation leaked into the output as a wrong number presented confidently. The design left precision deliberately open (§8, §11) and routed it here. A significant-digit rule behaves identically at every magnitude, `format(value, ".12g")` is standard library only, and 12 digits exceeds any precision a length, mass, or temperature conversion can honestly claim while sitting safely below where double artifacts appear. Confidence: high on the shape of the rule, medium on the exact digit count — a different count later is one superseding entry.

**R1000** — Every conversion result the tool prints — single-shot output and each successful batch result line (R6) — is formatted as `format(value, ".12g")`: at most 12 significant digits, trailing zeros stripped by the `g` conversion, so `0.1 km` to metres prints `100` and never `100.00000000000001`. The rule applies to results only; error messages echo the offending input as given (R4). It reproduces §13 S2's expected strings exactly (`212`, `373.15`).

Measurement, per the durable-evidence section of `docs/VISION.md` (a change nothing can observe is a change nobody can evaluate): no new mechanism is needed — the existing acceptance-script mechanism observes this once expected values are exact-match strings. The plan implementing R1000 must (a) pin the rule in unit tests, (b) write the S1 fixed-table acceptance script's expected outputs under this rule and include the ESC-1 case — `0.1 km` to `m` prints exactly `100` — as one of its rows, and (c) once merged, append the completing correction row for ESC-1 citing that script, which is the "expressed as an acceptance script" its pending check column asks for. Downstream: no plans exist yet; the plan covering the MVP `convert` milestone must list R1000 in its `covers`.

## OD-2 — HALTED: prettier output via the `rich` library

- **Date:** 2026-08-20
- **Evidence:** BL-3
- **Tenet relied on:** V5 — "No runtime dependency may be added: the Python standard library is the whole toolbox, and a diff that adds one violates this tenet."
- **What a decision would have said:** grant BL-3 — aligned, colored table output built on `rich`, as the owner filed it ("the `rich` library specifically"). Every route to that ruling adds `rich` as a runtime dependency, which is the diff V5 names as a violation; the evidence explicitly rules out the stdlib route by calling hand-rolled ANSI wasted effort, so no tenet-clean reading of BL-3 exists to grant.
- **What it needs from the owner:** the smallest change to `docs/VISION.md`: append an exception to V5 naming `rich` as a permitted presentation dependency (with the `docs/DECISIONS.md` approval entry the dependency rule in `AGENTS.md` requires); or rule directly — withdraw BL-3, or re-file it as stdlib-only aligned output, which would be decidable without touching V5.

BL-3 is owner-filed and V5 is owner-authored, so this is a conflict between two owner statements that only the owner can reconcile. Until then BL-3 stays in Proposed, nothing plans it, and the orchestrator must not act on it in any form — including a stdlib approximation, which the item as filed rejects.

## OD-3 — Currency conversion rejected; the design's non-goal stands

- **Date:** 2026-08-20
- **Evidence:** BL-4
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted."
- **Vision statements against:** (none — no statement in docs/VISION.md tells against this; the nearest in subject, V4, argues the same way, naming breadth of units as the thing to trade away.)
- **Alternatives considered:** (1) grant as filed, live rates fetched at run time — contradicts §3's explicit non-goal ("Currency, time zones, or any unit that needs live data") and R8's "fully offline and deterministic", and a fetched rate is a number the tool cannot verify: quietly wrong whenever the source is stale or unreachable, which is V1's worst output; (2) baked-in static rates — stays offline but drifts wrong from the day it ships, a confidently wrong number by design; (3) reject and leave the design unchanged — chosen.
- **Rationale:** The design already decided this: currency is a named non-goal (§3) and R8 requires offline determinism, both owner-landed. The owner's route to changing that exists — editing `docs/DESIGN.md`, which is theirs — but the oracle amending the design against its own non-goal on the strength of "feels half-finished" would trade correctness and simplicity for breadth, the exact trade V3 and V4 refuse. No behaviour changes under this ruling, so no new measurement is required — there is nothing downstream of it to observe.

## OD-4 — CLI syntax: `anvil <value> <from-unit> <to-unit>`; batch is explicit `--batch`; a bare `anvil` is a usage error

- **Date:** 2026-08-20
- **Evidence:** BL-5
- **Requirements added:** R1001
- **Requirements superseded:** (none)
- **Vision statement relied on:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently."
- **Vision statements against:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted." — it could be read as forbidding the `--batch` flag, since inferring batch mode from an empty argument list would be one less piece of interface. It does not forbid it: with implicit batch, R5 ("missing arguments: print usage and exit non-zero") and R6 ("read requests from standard input") both claim the same invocation, and a bare `anvil` at an interactive terminal would sit silently waiting on stdin — guessing silently, which V2 rejects. One explicit flag is the smaller total complexity; the collision of two requirements on one command line is the larger.
- **Alternatives considered:** (1) subcommand style, `anvil convert 5 km mi` — a second word of surface for a tool with exactly one verb, refused per V3; (2) other positional orders, `anvil km mi 5` or flag pairs `--from/--to` — the chosen order value, from-unit, to-unit reads as the user's own sentence ("5 km in miles", §4's use cases) and is the steward's filed default; nothing measurable separates the orders, so the tie goes to the default already on record; (3) batch as the bare no-argument invocation, the Unix filter convention (`cat`-like) — collides with R5 and hangs silently on a terminal, the direct V2 violation; (4) batch by detecting a non-tty stdin — behaviour would differ between a terminal and a script for the identical command line, an environment-dependent guess and untestable deterministically (R8's spirit); (5) batch as a `-` positional replacing the value — overloads the value slot with a mode sigil and still leaves bare `anvil` ambiguous.
- **Rationale:** BL-5 is the uncertainty class this ledger's opt-out exists for, but it is not vision-blind: the one load-bearing sub-question — what a bare `anvil` means — is exactly V2's case, and refusing loudly (usage to standard error, non-zero exit) beats waiting silently on stdin. The rest (positional order) the vision genuinely does not decide, so the steward's filed default stands, weighed in the alternatives above. Confidence: high on explicit `--batch` and on bare-`anvil`-is-an-error; medium on the positional order, where a later reversal is one superseding entry plus a mechanical rewrite of the Signatures block and two scripts — the HIGH-risk cost BL-5 itself names, which is why this is decided now rather than left to drift.

**R1001** — The `anvil` command line has exactly two valid shapes. **Single-shot:** three positional arguments in the order value, from-unit, to-unit — `anvil 5 km mi` — printing exactly the R1000-formatted result and a newline to standard output, and exiting zero. **Batch:** `anvil --batch` with no positional arguments, reading requests from standard input per R6. Every other invocation — missing, surplus, or unrecognised arguments, including a bare `anvil` with none — prints usage to standard error and exits non-zero (R5). R4 error messages also go to standard error. This fixes the invocation only; the batch line format (§11's third open question) is NOT decided here and must be filed as its own uncertainty by the plan covering the `convert-batch` milestone.

Measurement, per the durable-evidence section of `docs/VISION.md` (a change nothing can observe is a change nobody can evaluate): no new mechanism is needed — the acceptance scripts ARE the observation, since S1 and S3 execute these exact command lines and S3's missing/surplus cases pin the usage-error shape, including the bare `anvil` case, which the plan must include as an explicit S3 row. Downstream: the plan covering the MVP `convert` milestone lists R1001 in its `covers` alongside R1, R2, R4, R5, R1000, and its Signatures block and the S1/S3 scripts are now unblocked. Until the `convert-batch` milestone lands R6, `--batch` is an unrecognised argument and takes the usage-error path — consistent with this requirement, no special-casing in the MVP.

## OD-5 — Non-finite values are refused: `anvil` never prints `inf` or `nan` as a conversion result

- **Date:** 2026-08-20
- **Evidence:** BL-6
- **Requirements added:** R1002
- **Requirements superseded:** (none)
- **Vision statement relied on:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce."
- **Vision statements against:** V3 — "Simplicity comes before completeness: a small tool that is obviously right beats a large one that must be trusted." — it could be read as forbidding the extra branch: the smallest tool prints whatever the float arithmetic produced and adds no check. It does not forbid this: the branch is a few lines inside one function, while printing `inf`/`nan` grows the tool's *output surface* — every scripted consumer of R6 batch lines must now handle two tokens that look like results and are not — and V3 trades away completeness, never correctness, which is what the overflow case puts at stake.
- **Alternatives considered:** (1) print what the float math yields — `format(value, ".12g")` renders `inf` and `nan` happily, but `anvil 1e308 km mm` has a true mathematical answer (1e311) that a double cannot hold, so `inf` is a wrong number presented confidently, V1's named worst output, and `nan` propagates silently through a batch as if it were data; (2) refuse non-finite *inputs* but print overflow as `inf` — inconsistent, and it keeps the worse half: overflow is the case where finite, plausible inputs yield the wrong output; (3) avoid overflow with wider arithmetic (`decimal`/`fractions`, stdlib-only) — disproportionate machinery for a corner case, changes the R1000 formatting path, and V3 refuses it; (4) clamp to the largest finite float — a wrong number presented confidently, strictly worse than (1); (5) refuse both on the R4 path — the steward's filed default, chosen.
- **Rationale:** BL-6's two cases are one defect seen from two sides: a token that is not a number presented on the result channel. R4 already refuses "a value that is not a number", and `inf`/`nan` are exactly that in the sense a user means, whatever `float()` accepts; overflow is the same refusal applied to the output side, where V1 binds hardest because the inputs were innocent. The plan (`docs/plans/oracle/anvil-convert-mvp.md`) already proceeded on this default, so this ruling changes no code direction — it converts a LOW-risk guess into a landed requirement. Confidence: high; the reversal cost BL-6 itself names is a single branch.

**R1002** — The tool refuses, on the R4 error path (a message naming the offending input on standard error, non-zero exit): (a) an input value that parses to a non-finite float — `inf`, `-inf`, `nan`, in any spelling the parser accepts; and (b) a conversion of finite inputs whose result is non-finite (overflow). No conversion result the tool prints — single-shot, or a batch result line under R6 — is ever `inf` or `nan`; R1000's format rule applies to finite results only. Exact message wording stays with the plan, as R4 delegates it.

Measurement, per the durable-evidence section of `docs/VISION.md` (a change nothing can observe is a change nobody can evaluate): no new mechanism is needed — the acceptance-script mechanism observes this once `acceptance/S3.sh` executes both refusals. The MVP plan's slice-2 message table already carries the two rows (`anvil inf km m`, `anvil 1e308 km mm`), but its description of `acceptance/S3.sh` lists only the §13 cases and omits them; the plan implementing R1002 must (a) run both rows in `acceptance/S3.sh`, asserting non-zero exit and a message naming the offending input, and (b) pin both branches in unit tests. Downstream: `docs/plans/oracle/anvil-convert-mvp.md` adds R1002 to its `covers` and the one line adding the two rows to its S3 script section — no slice boundary, Signatures block, or S1 table changes, exactly as BL-6's LOW risk class predicted.
