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

_(filed by `/plan` or `/steward` when the design layer leaves a question open;_
_format:_ _`BL-<n>` — the question, the proposed default, HIGH or LOW risk, one_
_line on why that class, and `— filed by: plan`.)_

- **BL-5** — OD-1's measurement clause says "the plan that covers R1000 must
  make the rule observable twice", the second half being the S1 and S2
  acceptance scripts comparing the installed command's exact stdout, with the
  0.1 km → m row in S1's fixed table. A steward plan covering R1000 alone
  cannot deliver that half: no `anvil` command, no converter and no plan for
  either exists yet; S1 measures R1/R2 and S2 measures R3, none of which R1000
  delivers; and OD-1 explicitly leaves the exact CLI syntax open for a later
  planner, so writing `acceptance/S1.sh` now means deciding that syntax. A
  landed S1 script that invokes a command nobody has built also exits non-zero,
  which fails the required `acceptance-criteria` check on its own pull request
  and on every one after it until the CLI merges. So: which plan discharges
  the acceptance-script half of R1000's measurement? **Proposed default:** the
  R1000 steward plan delivers only the formatting rule and its blind unit tests
  asserting exact printed strings, including the ESC-1 reproduction (0.1 km → m
  prints exactly `100`), red against the artifact and green against the fix;
  the S1 and S2 scripts are delivered by the milestone plans that build the
  command they invoke — S1 by `convert`, S2 by `temperature` — each carrying
  OD-1's exact-stdout-string constraint verbatim and S1 carrying the 0.1 km → m
  row, and no acceptance script lands before the command it runs exists.
  **Risk: HIGH** — the answer decides whether the R1000 plan builds a
  command-line path at all, so it moves every slice boundary and Signatures
  block in it, it forces or defers a ruling on an external format OD-1 left
  open, and the wrong answer lands a red required check that blocks every later
  pull request — filed by: steward
