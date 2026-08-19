# grimsverk-anvil — test kit

This repository is a **test bed for
[grimsverk-template](https://github.com/GrimsVerk/grimsverk-template)**. The
project it builds (a tiny unit-conversion CLI) is throwaway; the point is to
run the template's unattended pipeline twice — once locally, once from a
Claude Code web session — on two isolated lanes in this one repository, and
compare.

The kit lives in `test-kit/` on `main`. During setup the template scaffold is
rendered into the same clone, beside it; `main` is then frozen as the common
starting point, and the two lanes (`run/local`, `run/web`) branch from it.

Start here, in this order:

1. `test-kit/TESTPLAN.md` — the whole protocol: owner setup (Part 1), rules
   for the testing agents (Part 2), what to compare (Part 3).
2. `test-kit/PROMPT-LOCAL.md` — paste into a local Claude Code session to
   start the local lane.
3. `test-kit/PROMPT-WEB.md` — paste into a Claude Code web session to start
   the web lane.
4. `test-kit/canned/` — the fixed inputs both lanes build from (DESIGN,
   VISION, BACKLOG, and a seeded escapes ledger); setup copies them into
   `docs/`. They were built from the template's own failure record as a
   **stress test**: deliberate design gaps, backlog items the pipeline must
   rule on / halt on / dismiss, a slug-collision trap, and criteria that
   should fail honestly at least once. The full bait map, with what each
   planted input is expected to trigger, is in TESTPLAN Part 3. Do not "fix"
   any of it.

The prerequisites this kit depends on are met: the template's per-base-branch
pipeline fix (ESC-46) is released as **v0.4.28**, and the evidence-recovery
tools the instructions use (`deliver-loop.sh --land-evidence`, the
setup-github transcript) as **v0.4.29**. Setup step 0 double-checks that the
latest release is at least v0.4.29 before anything is generated.
