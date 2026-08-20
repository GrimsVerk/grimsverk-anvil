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

## OD-6 — The `temperature` plan carries R7 and R8; the filed default stands

- **Date:** 2026-08-20
- **Evidence:** BL-7
- **Requirements added:** (none)
- **Requirements superseded:** (none)
- **Vision statement relied on:** (no vision statement decided this)
- **Vision statements against:** V6 — "A conversion that is numerically wrong, however plausible it looks, is rejected outright — as is any run that reports success while a criterion's evidence cell is empty or narrated rather than executed." — its second clause could be read as forbidding any arrangement under which R7 and R8 count as "covered" while no script can ever execute evidence for them. It does not forbid this: covered means planned, not passed — `coverage.sh`'s own output says so — and S4's row in `docs/acceptance.md` stays `pending / owner` under this ruling exactly as §13 assigned it, so no run reports success on S4's behalf. No other statement comes closer; the question is which plan's front matter names two ids, and the vision does not speak to plan bookkeeping.
- **Alternatives considered:** (1) the MVP `convert` plan carries them — the strongest rival, because R7's substance is actually built there: `pyproject.toml`'s `[project.scripts] anvil = ...` entry lands in that plan, its S1 and S3 scripts already run the installed command, and R8 holds from its first merge. Rejected because nothing measurable separates the two homes — both requirements are evidenced only by S4, which §13 marks (owner), so no acceptance script will ever execute them whichever plan claims them, and `coverage.sh` reports their absence from slice text as an expected non-functional absence either way — and moving them re-opens the critical-path MVP plan for a bookkeeping edit while the temperature plan already carries them. Honesty requires noting that BL-7's stated ground for the default is wrong: the temperature plan is NOT the first whose acceptance script runs the installed command end to end — S1 already does — but a weak argument for the default is not an argument against it when the alternatives tie. (2) Both plans list them — double attribution reads as both plans scheduling the same work, adds nothing one home lacks, and blurs which plan answers for them. (3) A dedicated non-functional plan — a plan whose slices deliver nothing, the horizontal layer `AGENTS.md` forbids. (4) Amend `docs/DESIGN.md` §12 to name them in a milestone — that document is the owner's, not mine to write.
- **Rationale:** BL-7 is pure coverage bookkeeping, and its LOW risk class is accurate: the answer's entire observable effect is one line of plan front matter, which flips R7 and R8 from "NOT PLANNED" to "covered" in `coverage.sh`'s report — the report the delivery loop branches on when deciding whether planning work remains. Where nothing measurable separates the candidates, the tie goes to the default already proceeded on — the same tiebreak OD-4 applied to the positional order. The temperature plan's claim is also true on its own terms: `acceptance/S2.sh` exercises the installed `anvil` console command, and the plan adds no dependency. Confidence: high that some single plan must carry them (the loop stalls on "unplanned" otherwise); the choice of which is low-stakes by construction, and reversing it is the one-line `docs/` pull request BL-7 itself names.

Measurement, per the durable-evidence section of `docs/VISION.md` (a change nothing can observe is a change nobody can evaluate): no new mechanism is needed — `coverage.sh` already observes exactly this ruling. Its report is the artifact that changes: `R7 covered by anvil-temperature`, `R8 covered by anvil-temperature`, with both listed under expected absences because §5 marks them `*(non-functional)*`. Verification of the requirements themselves stays where §13 put it: S4, the owner, on their own machine — this ruling assigns scheduling, never evidence. Downstream: zero diff. `docs/plans/oracle/anvil-temperature.md` already lists R7 and R8 in its `covers`, so no plan changes, no slice changes, and no script changes; this ruling converts the proceeded default into landed design-layer fact, and BL-7 leaves the uncertainties section by this citation.

## OD-7 — Batch line format: a request line is `<value> <from-unit> <to-unit>`; error lines print `anvil: line <n>: <reason>` on standard output, in stream order; exit 1 if any line failed

- **Date:** 2026-08-20
- **Evidence:** BL-8
- **Requirements added:** R1003
- **Requirements superseded:** (none)
- **Vision statement relied on:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently."
- **Vision statements against:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce." — it could be read as forbidding error text on standard output, since that puts non-result lines on the channel a scripted consumer parses as numbers. It does not forbid this: an error line can never read as a number — it begins `anvil: `, while R1000's format guarantees every finite result line begins with a digit or `-`, and R1002 guarantees every result line is finite — so a consumer that hits one breaks loudly at the exact line that failed. The arrangement V1 actually condemns is the diverted one: with error lines on standard error, a stdout-only consumer receives a silently shortened result list whose lines no longer align with its requests, and every number after the failure is a plausible-looking result attributed to the wrong request — confidently wrong, at scale.
- **Alternatives considered:** (1) error lines to standard error, matching R1001's single-shot convention — the strongest rival, and the Unix default. Rejected because it loses the property that carries the whole format: one output line per request, in input order. A stdout-only consumer (the common case: `anvil --batch < in > out`) gets fewer lines than requests with nothing marking where alignment broke — the silent misattribution V1 names — and the line-number prefix only rescues a consumer that merges both streams, which interleaves non-deterministically. The exit code says "something failed", never "which". (2) A malformed line (field count not three) treated as a usage error aborting the batch, exit 2 — one typo in a thousand-row pipe kills the run, directly against R6's "a bad line … does not stop the remaining lines"; a bad line is data, not invocation shape. (3) Blank lines as errors rather than skipped — makes the trailing newline every editor and heredoc emits a failed batch; skipping is safe precisely because a skipped line produces no output line, so nothing misaligns, and the line-number prefix keeps traceability. (4) A comma- or CSV-shaped grammar — a second grammar for the same three tokens the command line already takes; whitespace-separated fields make a request line exactly the argument tail of the single-shot call, one thing to document and one parser to test. (5) A distinct exit code for batch failure (3) — a third code answering no question a consumer asks; reusing 1 keeps "a conversion was refused" meaning the same thing in both modes, and 2 stays R1001's shape-of-invocation error. (6) Echoing the offending line in the error prefix instead of numbering — duplicates arbitrary input into output, still ambiguous when two identical lines differ in fate; the 1-based line number is short, unique, and survives blank-line skipping.
- **Rationale:** BL-8 is the uncertainty OD-4 ordered filed: the design leaves the batch line format deliberately open (§11, owner test note) and routes it here. The filed default is coherent with everything landed — R1001's token order, the MVP plan's exit-code split (1 refused, 2 usage), the MVP's exact reason texts — and the one sub-question with real vision weight, the stream, is V2's case: a failure a consumer can fail to see is a silent guess, and the single ordered stream is the arrangement in which failure is loudest at the point it happened. The load-bearing property is: every request yields exactly one output line, in input order; blanks are not requests. Confidence: high on the grammar, the stream, blank-line skipping, and the exit codes; medium on the exact error-line prefix wording, which stays with the plan exactly as R4's wording does — before S5 lands a wording change is a plan edit, after it, one superseding entry.

**R1003** — Batch mode (`anvil --batch`, R1001) reads standard input line by line and writes to **standard output**, in input order, exactly one line per request. A **request line** is three fields — value, from-unit, to-unit, the R1001 order — separated by runs of whitespace, leading and trailing whitespace ignored. A blank or whitespace-only line is not a request: it is skipped, produces no output line, and is not a failure. A request that converts prints its R1000-formatted result, byte-identical to the same conversion run single-shot. A request that is refused — any R4/R1002 reason, or a line whose field count is not three, which is one new reason — prints `anvil: line <n>: <reason>`, where `<n>` is the 1-based input line number (skipped blank lines still count toward it) and `<reason>` is the same text the single-shot path prints for the same refusal. The new malformed-line reason's exact wording stays with the plan, as R4 delegates wording, but it must name the offending input — §13 S5 requires the error line to do so. Per-request diagnostics never go to standard error; standard error remains R1001's usage-error channel, exercised before batch reading starts. Exit code: 0 when no request failed — an empty standard input is a successful batch of zero requests — and 1 when any request failed; 2 remains R1001's usage-error path (for example `anvil --batch extra`).

Measurement, per the durable-evidence section of `docs/VISION.md` (a change nothing can observe is a change nobody can evaluate): no new mechanism is needed — `acceptance/S5.sh` is the observation once written, and this ruling fixes every expected byte in it. The plan covering the `convert-batch` milestone must make S5 (a) run §13's five-line mixed batch exact-match, with the error line asserted in its stream position, not merely present; (b) include a blank line, pinning both the skip (no output line) and the numbering (the error's `<n>` counts the blank); (c) include a malformed wrong-field-count line; (d) assert exit 1 for the mixed batch and exit 0 for an all-good batch; and (e) assert at least one batch result line byte-identical to the single-shot output of the same conversion. Unit tests pin the line parser, the numbering, and the empty-input case. Downstream: this unblocks the `convert-batch` plan — the Signatures block for the batch entry point and `acceptance/S5.sh` were both waiting on this ruling, per BL-8 — and that plan lists R6 and R1003 in its `covers`. No landed plan changes: the MVP and temperature plans are untouched. BL-8 leaves the uncertainties section by this citation.

## OD-8 — Undecodable batch input: standard input is decoded with `errors="replace"`, and an affected line refuses like any other bad line

- **Date:** 2026-08-20
- **Evidence:** BL-9
- **Requirements added:** R1004
- **Requirements superseded:** (none)
- **Vision statement relied on:** V2 — "Clear, honest errors come before feature breadth: refusing loudly beats guessing silently."
- **Vision statements against:** V1 — "Correct conversions come before everything else: a wrong number presented confidently is the worst output this tool can produce." — it could be read as forbidding replacement, because the error line for an affected request echoes U+FFFD rather than the bytes the user actually sent: an inexact echo presented as "the offending input" (R4). It does not forbid this: the inexactness is confined to the error channel and can never reach the result channel — a field carrying U+FFFD matches no unit symbol and parses as no float, so a replaced line can only refuse, never convert — and the echo is as faithful as any text the tool can print, since the offending bytes have no exact representation on a text stream in the first place. What V1 actually condemns here is the traceback path, where the batch dies mid-stream and every request after the bad byte silently gets no answer at all.
- **Alternatives considered:** (1) Status quo — strict text-mode standard input: `UnicodeDecodeError` ends the batch with a Python traceback, no output line for that request, every later line unprocessed (directly against R6's "a bad line … does not stop the remaining lines"), and an exit code the tool did not choose — failing obscurely, the opposite of V2's refusing loudly. (2) Catch the decode error around the read loop and end the batch with a clean message — better dressing on the same R6 violation: the remaining lines still die with it, and text-mode decoding gives no reliable way to resume after the bad byte. (3) Read `sys.stdin.buffer` and decode each line strictly, refusing an undecodable line with a new dedicated reason ("not valid UTF-8: …") — the loudest and most byte-faithful option, but it adds a new reason to R1003's output grammar, buffer-and-split machinery for a corner case, and expected content S5 would then owe coverage for; V3 refuses that when option (5) buys the same per-line refusal in one argument to one call, because a newline byte never occurs inside a multi-byte UTF-8 sequence, so replacement preserves line structure exactly. (4) Skip undecodable lines the way blank lines are skipped — silent data loss: a request the user sent produces no output line and no failure, V2's guessing silently. (5) Decode with `errors="replace"` — the steward's filed default, chosen: the affected line survives as a line, lands on the existing refusal reasons with its correct line number, and every later line still runs.
- **Rationale:** BL-9 is the one gap OD-7 left: R1003 fixes every byte of the batch contract but assumes every input line decodes, and Python's default turns the first undecodable byte into the exact failure shape R6 forbids — stopped batch, missing output lines, foreign exit code. Replacement makes the failure ordinary instead of fatal: U+FFFD cannot form a unit or a number, so the affected line refuses through `unknown unit`, `not a number` or `malformed line`, whichever fits, with no new shape anywhere. The plan (`docs/plans/oracle/anvil-convert-batch.md`) already proceeded on this default, so this ruling changes no code direction — like OD-5, it converts a LOW-risk guess into a landed requirement. Confidence: high; the reversal cost BL-9 itself names is one argument in one call in `main`.

**R1004** — In batch mode (R1001, R1003), standard input is decoded as UTF-8 with `errors="replace"`: undecodable bytes become the replacement character U+FFFD and never terminate the batch. A line so affected is refused through the ordinary R1003 error path with an existing reason — a field containing U+FFFD can never name a unit nor parse as a value, so such a line never converts — and every later line is still processed. No new reason text, no new exit code, no new output shape; the batch's exit code remains R1003's own (1 if any request failed). The tool never exits on undecodable input with a traceback. Single-shot arguments are outside this requirement: they reach the tool already decoded by the operating system.

Measurement, per the durable-evidence section of `docs/VISION.md` (a change nothing can observe is a change nobody can evaluate): no new mechanism is needed, but the existing one must actually exercise the path — the offline test suite, which CI runs on every pull request. Driving `run_batch` with already-decoded strings cannot observe this, because the decode happens in `main` before `run_batch` sees anything; the plan implementing R1004 must therefore pin it in unit tests that drive `main(["--batch"])` with real undecodable bytes on a patched binary standard input (for example `b"\xff km m\n1 mi km\n"`), asserting the error line for the affected request under an existing reason, the later line's correct result, exit 1, and an empty standard error. `acceptance/S5.sh` is untouched: no expected byte changes, exactly as BL-9's LOW risk class stated. Downstream: `docs/plans/oracle/anvil-convert-batch.md` adds R1004 to its `covers` and the test rows above — its slice 1 already reads standard input with `errors="replace"`, so no slice boundary, Signatures block or acceptance script moves. BL-9 leaves the uncertainties section by this citation.
