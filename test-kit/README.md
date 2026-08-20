# grimsverk-anvil — test kit

This repository is a **test bed for
[grimsverk-template](https://github.com/GrimsVerk/grimsverk-template)**. The
project it builds (a tiny unit-conversion CLI) is throwaway; the point is to
run the template's unattended pipeline twice — once locally, once from a
Claude Code web session — on two isolated lanes in this one repository, and
compare.

**`main` carries this kit and nothing else, forever.** The owner pastes two
prompts and leaves. Each agent branches off `main` to its own lane
(`run/local`, `run/web`), renders its OWN scaffold there with copier, does its
own setup, runs its own driver, and never touches `main` or the other lane.
Between rounds the owner deletes every branch except `main`.

Start here, in this order:

1. `test-kit/TESTPLAN.md` — the whole protocol: the one-time rig (Part 0,
   already done), lane setup each agent performs itself (Part 1), rules for
   the testing agents (Part 2), what the owner compares (Part 3).
2. `test-kit/PROMPT-LOCAL.md` — paste into a local Claude Code session.
3. `test-kit/PROMPT-WEB.md` — paste into a Claude Code web session created
   with BOTH repositories attached: this one to work in, the template so
   copier can read it (template ESC-50: a web session can never mint as the
   App, so copier rides the owner's injected credential instead).
4. `test-kit/canned/` — the fixed inputs both lanes copy into `docs/`
   (DESIGN, VISION, BACKLOG, a seeded escapes ledger). Built from the
   template's own failure record as a **stress test**: deliberate design
   gaps, backlog items the pipeline must rule on / halt on / dismiss, a
   slug-collision trap, and criteria that should fail honestly at least once.
   The bait map is in TESTPLAN Part 3. Do not "fix" any of it.

Prerequisite releases, all met and pinned by Part 1 step 2: per-base lanes
(v0.4.28), evidence recovery (v0.4.29), App-only credentials — two secrets
total, zero PATs (v0.4.30), the round-1 blocker fixes — born-red `uv.lock`
flow, wrong-ref CODEOWNERS probe (v0.4.31), the first-commit mypy hook fix —
ESC-49 (v0.4.32), the server-side pull-request opener for web sessions —
ESC-50 (v0.4.33), REST-only session reads — ESC-51 (v0.4.34), the round-2.1
batch — ESC-52..55 plus local F5/F6/F7 (v0.4.35), round 3's five —
ESC-56..60 (v0.4.36), and the id-namespace leak both lanes caught identically
— ESC-61 (**v0.4.37**).
