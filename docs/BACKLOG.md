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

- **BL-5** — The command-line invocation syntax for `anvil`. The plan
  implementing OD-1 / R1000 is the plan covering the MVP `convert` milestone
  (R1, R2, R4, R5), and it cannot declare a Signatures block or write the S1
  and S3 acceptance scripts until the syntax is fixed: the positional order,
  and how batch mode is invoked — the second decides whether a bare `anvil`
  with no arguments is a usage error under R5 or a request to read standard
  input. `docs/DESIGN.md` §8 and §11 record both as deliberately not decided
  there, and the design's owner-authored test note says the planning layer must
  file them rather than settle them. **Proposed default:** three positionals in
  the order value, from-unit, to-unit — `anvil 5 km mi` — printing the result
  as the bare formatted number on one line (that part R1000 already decides);
  batch mode invoked by an explicit `--batch` flag that reads standard input
  and takes no positionals; any other shape — missing, surplus, or unrecognised
  arguments — prints usage to standard error and exits non-zero.
  **Risk: HIGH** — it is the tool's external interface, so it fixes every
  Signatures block in the plan and the exact command lines S1 and S3 execute,
  and changing it after the fact rewrites the CLI slice and both acceptance
  scripts — filed by: steward
- **BL-6** — Non-finite values in `anvil`. Two cases the design layer does not
  reach: a value that parses to a non-finite float (`anvil inf km m`,
  `anvil nan km m`), and a conversion of finite inputs whose result overflows to
  infinity (`anvil 1e308 km mm`). R1000 says every printed result is
  `format(value, ".12g")`, which prints `inf` and `nan` as results; R4 covers "a
  value that is not a number", which reads onto `nan` but not onto overflow.
  **Proposed default:** refuse both on the R4 path — an error naming the
  offending input on standard error, exit non-zero — so the tool never prints
  `inf` or `nan` as a conversion result, per the vision's refusal of a
  confidently wrong number. **Risk: LOW** — every candidate answer is a single
  branch inside the converter; it moves no slice boundary, changes no Signatures
  block, alters no acceptance script's fixed table, and is a few lines to
  reverse. Proceeded on the default in `docs/plans/oracle/anvil-convert-mvp.md`
  — filed by: steward
