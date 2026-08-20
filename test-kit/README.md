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
ESC-56..60 (v0.4.36), the id-namespace leak both lanes caught identically —
ESC-61 (v0.4.37), the updater's lane blindness and its unapprovable pull
request — ESC-62/63 (v0.4.38), round 3.2's four — ESC-64..67, the
livelock stop among them (v0.4.39), and round 3.3's six — ESC-68..73, which
end with the discovery that a private repository's gates may be configured
and binding nothing (v0.4.41), and round 3.4's four — the budget ceiling that
re-zeroed itself on a rounded timestamp, a killed run reported as success,
readiness blind to the debris the driver refuses on, and two inert tool grants
that camouflaged real errors — ESC-74..77 (v0.4.42) — and the three the web
lane's top-severity finding produced: a stop-time branch sweep, gating one lane
no longer ungating the other, and a refusal to arm auto-merge on an unprotected
base rather than merging on the spot — ESC-78..80 (v0.4.43) — and the one that
explains a run dying with no cause at all: two drivers on one machine were
indistinguishable, so one operator's pattern kill reached into the other
project — ESC-81 (v0.4.44) — and the deadlock that stopped a lane at SETUP with
no legal move left, where one required check demanded a document be append-only
and another scanned that whole document for format errors — ESC-82
(**v0.4.45**).
