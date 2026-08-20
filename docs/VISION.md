# Vision — grimsverk-anvil

**Not requirements.** `docs/DESIGN.md` says what gets built; this file says what
matters when two reasonable designs disagree. It is the tiebreaker an agent
reaches for when the evidence is genuinely ambiguous and nobody is awake to ask.

`CODEOWNERS` puts this file behind the owner, and that is not a restriction
bolted on — it is the mechanism. The oracle names, in every decision it writes,
the statement here that it leaned on (`docs/DESIGN.oracle.md`). When a decision
comes out wrong, the owner edits the statement rather than arguing with the
decision, and every future decision moves with it.

## What this project is for

grimsverk-anvil exists to prove, on a real overnight run, that the
grimsverk-template pipeline works end to end — and, as a side effect, to leave
behind a small unit-conversion CLI that answers instantly and offline. If the
pipeline builds it without a human touching anything mid-run, the project
worked; the CLI itself is the anvil the hammer is tested on.

## Priorities, in order

- **V1** — Correct conversions come before everything else: a wrong number
  presented confidently is the worst output this tool can produce.
- **V2** — Clear, honest errors come before feature breadth: refusing loudly
  beats guessing silently.
- **V3** — Simplicity comes before completeness: a small tool that is obviously
  right beats a large one that must be trusted.

## What I would trade away

- **V4** — Breadth of units is expendable: dropping exotic units, aliases, or
  whole categories is always an acceptable price for correctness, clarity, or
  simplicity.

## Core tenets

- **V5** — No runtime dependency may be added: the Python standard library is
  the whole toolbox, and a diff that adds one violates this tenet.

## Durable evidence is a requirement, not a nicety

**This section is not a question for you to answer.** It is a statement about
how unattended operation works here, kept in the vision file for one reason:
the oracle must be able to *cite* it. A decision to add a measurement needs
something in this document standing behind it, and without this section there
is nothing.

The owner's ruling, in their words:

> the data needs to be collected in a sensible way so that future runs can be
> improved by not repeating mistakes… if a change is necessary in an unattended
> run that goes outside or misses built in data collection mechanisms, then new
> data collection mechanisms need to be added to track the performance of the
> changes that are downstream of the oracle's ruling.

What follows from it, and what is already built:

- **A run leaves a record.** `docs/runs/<timestamp>/run.md` — committed, on its
  own pull request, at every stop whatever the reason. The run log used to be
  gitignored, and in a web session it lived in a container that is reclaimed, so
  the evidence that would tell the next run what went wrong was destroyed by
  default.
- **The review gate keeps what it was shown and what it said.**
  `docs/runs/<timestamp>/reviews/` holds the payload and the reply for every
  review in that run. It is the only load-bearing gate with no fixtures, and it
  was also the only one leaving no trace to build fixtures from.
- **A change nothing can observe is a change nobody can evaluate.** When a
  decision alters behaviour that no existing check, test, run report or review
  artifact would notice, adding the thing that notices is part of the decision —
  not a follow-up, and not optional. This is what the owner's ruling means by
  measurements "downstream of the oracle's ruling", and an oracle decision may
  cite this statement to justify adding one.

**On space.** Committed evidence grows, and the owner has weighed that
deliberately: *"i would rather risk gathering too much data and deal with space
issues, than getting stuck without the info to get out of it."* A space problem
is visible, bounded and fixable later; missing evidence is none of those. If it
becomes a problem the answer is a retention rule — prune payloads older than N
runs, keep every verdict — and never a return to discarding them.

## What makes an answer unacceptable

- **V6** — A conversion that is numerically wrong, however plausible it looks,
  is rejected outright — as is any run that reports success while a criterion's
  evidence cell is empty or narrated rather than executed.
