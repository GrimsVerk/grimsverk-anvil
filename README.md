# grimsverk-anvil — test prep branch

This repository is a **test bed for
[grimsverk-template](https://github.com/GrimsVerk/grimsverk-template)**. The
project it will build (a tiny unit-conversion CLI) is throwaway; the point is
to run the template's unattended pipeline twice — once locally, once from a
Claude Code web session — on two isolated lanes in this one repository, and
compare.

This branch (`claude/grimsverk-anvil-test-prep-86r4xu`) carries only the test
kit. `main` receives the generated scaffold during setup and is then frozen as
the common starting point for both lanes.

Start here, in this order:

1. `test-kit/TESTPLAN.md` — the whole protocol: owner setup (Part 1), rules
   for the testing agents (Part 2), what to compare (Part 3).
2. `test-kit/PROMPT-LOCAL.md` — paste into a local Claude Code session to
   start the local lane.
3. `test-kit/PROMPT-WEB.md` — paste into a Claude Code web session to start
   the web lane.
4. `test-kit/canned/` — the fixed design documents (DESIGN, VISION, BACKLOG)
   both lanes build from; setup copies them into `docs/` on `main`. The design
   contains two deliberate gaps and two seeded backlog items — that is the
   oracle bait; do not "fix" it.

Hard prerequisite: the template fix "Scope the one-PR rule per base branch"
(ESC-46) must be merged and released in grimsverk-template before setup step 1,
or the two lanes will collide.
