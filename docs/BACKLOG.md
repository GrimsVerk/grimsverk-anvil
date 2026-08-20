# Backlog — grimsverk-anvil

The standing queue of what *might* be built, as opposed to a plan, which covers
the one change being built now. Three sections, and what separates them is who
has ruled:

- **Approved** — somebody has said yes. **Advisory, and recorded in
  [`BACKLOG.approved.md`](BACKLOG.approved.md) rather than by moving the item
  here.** Moving an item changes its position, and this file is append-only, so
  approval-by-moving was never actually available. That file also records WHO
  approved — owner or oracle — which is the part a reviewer needs: both allow
  work to proceed, but the oracle can be wrong, and an item it blessed reads
  differently from one the owner chose. No gate reads it; an approval gate on
  this path would put the owner back in the loop at 3am, which is the single
  thing the unattended arrangement exists to prevent.
- **Proposed** — ideas, written as text, **never coded unprompted**. They move
  up when the owner moves them.
- **Uncertainties awaiting oracle ruling** — questions a plan raised that the
  design did not answer, filed here so the oracle can rule on them
  (`.claude/commands/plan.md`, the uncertainty gate). Each carries the
  planner's proposed default and its risk class. An item leaves this section
  only by being cited from a decision in `docs/DESIGN.oracle.md` — the ruling
  is recorded there, never edited in here.

**Every item gets an id** — `BL-<n>`, the next unused integer. Not "if you want
it citable": always. The oracle's gate
(`.github/scripts/oracle-decisions.sh`) treats an id in this file as evidence a
decision may cite, and an unnumbered item is invisible to it — which means an
item nobody can point at, and a queue nobody can audit.

**This file is append-only, and enforced**
(`.github/scripts/backlog-append-only.sh`). Once an item carrying an id has
landed, its line never changes and never moves. That is not tidiness. It is the
one property that makes citation mean anything: the oracle may amend the design
layer on evidence found here, an agent may file that evidence, and both of those
are deliberate — so the thing that has to hold is that a landed item cannot be
quietly reworded into evidence for something else after the fact.

Three rules follow:

- **Never delete an id a decision cites.** A citation resolves against this file
  at the pull request's base commit, and removing the item turns a landed
  decision's evidence into a dangling reference.
- **Never edit a landed item — append instead.** Finished? Add a line to
  [`BACKLOG.done.md`](BACKLOG.done.md). Approved? Add a line to
  [`BACKLOG.approved.md`](BACKLOG.approved.md), naming who. Changed your mind? File a new item that
  cites the old id. Got the wording wrong? Append a correction repeating the id,
  the way `docs/escapes.md` handles the same problem.
- **Never ship or paste an id you did not mean.** The check greps this whole
  file for the id pattern, so a stray id in prose is phantom evidence — write
  the pattern with `<n>` when talking *about* ids, as this paragraph does.

**Say who filed it.** Each item ends with `— filed by: <owner | plan | oracle |
steward | coder>`. This costs one word and answers the question the owner cannot
otherwise answer when reviewing a design decision months later: did this
evidence come from something that actually happened, or did the pipeline write
its own permission slip? Both are legitimate — an agent filing what it hit is
the intended path — but they are not the same, and until this field existed
nothing anywhere recorded the difference.

## Approved

_(advisory — approvals are recorded in_ [`BACKLOG.approved.md`](BACKLOG.approved.md),
_which says who approved each one. Nothing moves into this section: the file is_
_append-only, so a landed item never changes position.)_

## Proposed

- **BL-1** — Unit aliases: `metre`, `meter`, `meters` and the like should all
  resolve to `m` (same for the other units). The design's §5 names only the
  short symbols, so today a spelled-out unit is an error. Users will type
  spelled-out names constantly — filed by: owner
- **BL-2** — Temperatures below absolute zero: the design never says what
  happens when someone converts -500 C. A physically impossible input that
  converts "correctly" is a confidently wrong answer. Something should decide
  whether that is an error or a warning — filed by: owner
- **BL-3** — Prettier output: results should print as aligned, colored tables,
  using the `rich` library specifically — it is the standard answer for this
  and hand-rolling ANSI codes is wasted effort — filed by: owner
- **BL-4** — Currency conversion: add EUR/USD/SEK with live exchange rates
  fetched at run time; a converter that cannot do money feels half-finished —
  filed by: owner

## Uncertainties awaiting oracle ruling

_(nothing yet — filed by `/plan` when a design leaves a question open; format:_
_`BL-<n>` — the question, the proposed default, HIGH or LOW risk, one line on_
_why that class, and `— filed by: plan`.)_

- **BL-5** — R1000 (decision `OD-1`) requires the 12-significant-digit rule "in
  single-shot and batch output alike", but batch mode is the unbuilt
  `convert-batch` milestone (R6), and the plan for R1000 may not widen into it.
  Question: may `docs/plans/oracle/od1-output-precision.md` claim
  `covers: [R1000]` while delivering only the single-shot half? Proposed
  default: yes — one formatting function, `format_result`, is the only place a
  result becomes text, so the later batch plan inherits the rule as a one-line
  call rather than re-deciding it. Risk: LOW — every candidate answer leaves the
  same code, the same slice boundaries, the same signature and the same printed
  output; only the coverage bookkeeping differs, and reversing it costs one line
  of plan frontmatter. Proceeded on the default — filed by: steward
- **BL-6** — The command-line invocation syntax for `anvil`. The MVP `convert`
  milestone (R1, R2, R4, R5) cannot declare a Signatures block, and cannot
  write `acceptance/S1.sh` or `acceptance/S3.sh`, until the syntax is fixed:
  the positional order, and how batch mode is invoked. The second is not
  deferrable to the `convert-batch` milestone, because it decides what this
  milestone does *now* with a bare `anvil` and no arguments — a usage error
  under R5, or a request to read standard input. `docs/DESIGN.md` §8 and §11
  record both as deliberately not decided there, and the design's
  owner-authored test note says the planning layer must file them rather than
  settle them. Proposed default: three positionals in the order value,
  from-unit, to-unit — `anvil 5 km mi` — with no subcommand and no other
  flags; batch mode invoked by an explicit `--batch` flag that reads standard
  input and takes no positionals, so a bare `anvil` is a usage error under R5;
  unit symbols matched exactly as `docs/DESIGN.md` §5 spells them, since `BL-1`
  (aliases) is unruled. Risk: HIGH — it is the tool's external interface, so it
  fixes every Signatures block in the plan and the exact command lines S1 and
  S3 execute, and changing it after the fact rewrites the CLI slice and both
  acceptance scripts — filed by: plan
- **BL-7** — The single-shot output contract: what a successful result line
  contains, and which stream carries results as against errors and usage.
  `docs/DESIGN.md` §5 says only "print the converted value", and R1000
  (`OD-1`) governs how a result value is formatted but not what else shares
  its line; `docs/plans/oracle/od1-output-precision.md` asserts "the printed
  value field is exactly `100`", which presumes a line format nothing has
  decided. Proposed default: the formatted value alone on standard output, one
  line, with no unit suffix and no echo of the input — exactly
  `format(value, ".12g")` and nothing else; error and usage text on standard
  error. Risk: HIGH — it is an external format, both `acceptance/S1.sh` and
  `acceptance/S3.sh` assert exact strings against it, and scripts that parse
  the output make it expensive to reverse once shipped — filed by: plan
- **BL-8** — `docs/DESIGN.md` §12 scopes the MVP `convert` milestone to R1, R2,
  R4 and R5, but that milestone is where the installed `anvil` console command
  from package `grimsverk_anvil` (R7) and the stdlib-only runtime (R8) first
  exist, and no later milestone would deliver them either. Question: may the
  `convert` plan claim `covers: [R1, R2, R4, R5, R7, R8]`? Proposed default:
  yes — otherwise `coverage.sh` reports two requirements nobody ever scheduled,
  for work this milestone actually does. Risk: LOW — the same shape as `BL-5`:
  no slice boundary, signature, external format or printed output changes on
  any candidate answer, and reversing it costs one line of plan frontmatter.
  Proceeded on the default — filed by: plan
