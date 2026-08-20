# Unattended run report — web frontend, round 3.1

- Run id: `20260820T022911Z`
- Started: 2026-08-20T02:29:11Z
- Stopped: 2026-08-20T02:40Z
- Frontend: `/deliver-loop` web mode, template **v0.4.36**
- **THIS RUN'S BASE BRANCH: `run/web`** — every pull request this run opened
  merges into it, and this run waited only on pull requests targeting it.
- Limits set by the owner: 30 pull requests, 12 wall-clock hours, 60
  iterations. Used: **1 pull request, ~11 minutes, 1 iteration.**
- Budget: no usage gauge is reachable in a web session, by design (ESC-50).
- Stop reason: **a required check is red for a defect in a template-owned
  document, and the fix is in a CODEOWNERS-owned path this run may not touch.**

## What ran

| # | Phase | Outcome |
| --- | --- | --- |
| — | setup | Rendered at `_commit: v0.4.36`; base branch gated in 3 minutes; `unattended-ready.sh --runtime` GREEN. |
| 1 | ORACLE | Oracle worker, 6m43s, exit 0, 1 commit: `docs/DESIGN.oracle.md` +47, `docs/oracle/handoff-2026-08-20-1.md` +40. |
| 1 | open | **PR #7 opened by `autogrims[bot]`** — the App — with `.pr-request.json` retained, which ESC-56 now permits. |
| 1 | WAIT | `plan` red at step 5, `escape-refs`. Run stopped. |

## What the oracle produced

The same three rulings as round 3, independently regenerated — a useful
reproducibility signal:

- **OD-1** (evidence ESC-1) adds **R1000**: values print via
  `format(value, '.12g')`, so `0.1 km` in metres prints `100`.
- **OD-2** (evidence BL-4) declines currency conversion; the offline non-goal
  stands.
- **OD-3** (evidence BL-3) **HALTS**: `rich` cannot be reconciled with vision
  tenet V5, and the owner is told what to change in either direction.

## Why the run stopped

`AGENTS.md`, as shipped by v0.4.36, contains:

> or the opener's `.pr-request.json` marker (the one non-document member — the
> pull-request machinery a driver without App identity must commit, ESC-53/56)

`escape-refs.sh` scans `AGENTS.md` and resolves every `ESC-<n>` in it against
**this project's** `docs/escapes.md`. `ESC-53` lives in the *template's* ledger,
not the project's, so the citation dangles and the required `plan` check fails:

```
escape-refs: citation(s) that do not resolve at the base commit:
  AGENTS.md cites ESC-53
```

This is not specific to this repository. A clean scaffold rendered from the same
release into an empty directory ships an **empty** `docs/escapes.md` and an
`AGENTS.md` citing `ESC-53` — so **every project generated from v0.4.36 fails
its own `plan` check on its first pull request.**

It is also a regression from the fix to the previous round's blocker: on
v0.4.35 this step passed ("1 citation(s) across 3 document(s), all resolve").
The prose added to explain ESC-56 introduced the citation.

Fixing it means editing `AGENTS.md`, which is CODEOWNERS-owned and off-limits.
Adding a stub `ESC-53` row to this project's ledger would fabricate an escape
that never happened here — the thing `AGENTS.md` most explicitly forbids. So
the run stops and reports.

## Progress since round 3

- **ESC-56 confirmed working.** `plan-resolve.sh` now names the marker among
  its exempt paths and returns 0 with it in place; the `plan` job's steps 3 and
  4 pass. Round 3's forced deviation (deleting the marker) is retired.
- **ESC-57 not yet observable** — the CODEOWNERS step is skipped once step 5
  fails.

## Anomalies worth the owner's attention

- A web session still cannot read CI job logs or download artifacts (the proxy
  refuses the storage host), so the review payloads below are `MISSING.md`
  markers rather than content, and this diagnosis was again reached by reading
  the workflow and reproducing the step locally.

## What remains

The oracle's three rulings are open on PR #7 and unmerged. No plan, no code, no
acceptance. The run resumes cleanly from `PHASE=ORACLE` once `plan` can pass.
