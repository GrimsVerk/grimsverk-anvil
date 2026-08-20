# Unattended run report — web frontend, round 2.1

- Run id: `20260819T233920Z`
- Started: 2026-08-19T23:39:20Z
- Stopped: 2026-08-19T23:45Z
- Frontend: `/deliver-loop` web mode, template **v0.4.34** (ESC-51)
- **THIS RUN'S BASE BRANCH: `run/web`** — every pull request this run opens
  merges into it, and this run waits only on pull requests targeting it.
- Stop reason: **SETUP refusal**, one defect narrower than round 4.
  `unattended-ready.sh --runtime` now reads everything it needs over REST and
  confirms all seven gates bind on `run/web`, then refuses on its credential
  liveness probe, which still uses `gh auth status` — the one command that
  reports failure on this platform.
- Limits set by the owner: 30 pull requests, 12 wall-clock hours, 60
  iterations. None reached; the run stopped at preflight, not on a limit.
- Budget: no usage gauge is reachable in a web session, by design (ESC-50).
  The countable limits above stand in for the local lane's 20% weekly ceiling.

## What v0.4.34 fixed

ESC-51 fixed the round-4 blocker's first half, and the fix is confirmed good.
The readiness check resolves the repository over REST and reads the live
ruleset: the pull-request rule and all seven required checks (`plan`,
`template-sync`, `secrets`, `test-the-tests`, `acceptance-criteria`, `review`,
`checks`) are reported binding on `run/web`. The scaffold rendered clean at
`_commit: v0.4.34`, `uv sync` passed, the commit's hooks passed.

## What still stops the run

1. **The credential probe.** `unattended-ready.sh:246` still branches on
   `gh auth status`, which fails on a platform whose proxy injects the
   credential — so the check refuses with "no GitHub identity works here …
   gh holds no login at all" while `gh api user` returns `GrimsVerk`. One
   line; `gh api user` is the fix.
2. **No pull request can be opened.** The ESC-50 server-side opener is
   unreachable two ways: this credential has no `actions: write` (403 on a
   registered workflow), and `open-pr.yml` is dispatch-only so it never
   registers, because `main` carries no `.github/`. The forbidden fallback —
   opening the pull request under the owner's ambient login — was not used.

## Anomalies worth the owner's attention

- **The ruleset does not hold against this session.** A direct push to the
  gated base branch succeeded with GitHub reporting "Bypassed rule
  violations". The web lane holds the owner's admin credential, so it is
  stronger than the test's design assumes, not weaker. Probe reverted
  immediately; the lane is at its clean scaffold commit.
- v0.4.34 tells the driver never to use `gh` porcelain, and two lines earlier
  prescribes `gh workflow run` for opening pull requests.

## What remains

Everything. Zero iterations, zero pull requests, no oracle ruling, no plan, no
feature, no acceptance run. The detector is correct and ready —
`PHASE=ORACLE BASE=run/web REASON=evidence UNCITED=BL-3 BL-4 ESC-1`.
