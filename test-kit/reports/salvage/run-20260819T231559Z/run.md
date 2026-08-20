# Unattended run report — web frontend

- Run id: `20260819T231559Z`
- Started: 2026-08-19T23:15:59Z
- Stopped: 2026-08-19T23:29Z
- Frontend: `/deliver-loop` web mode (Claude Code web session)
- **THIS RUN'S BASE BRANCH: `run/web`** — every pull request this run opens
  merges into it, and this run waits only on pull requests targeting it.
- Stop reason: **SETUP refusal.** `.github/scripts/unattended-ready.sh
  --runtime` cannot complete in a hosted web session. Preflight (step 2 of the
  command file) never passed, so no iteration ever ran.
- Limits the owner set in advance: max 30 pull requests, max 12 wall-clock
  hours, max 60 iterations. None was reached or approached — the run stopped
  on the setup refusal, not on a limit.

## What ran

| Step | Result |
| --- | --- |
| Base branch established, first turn, out loud | `run/web`. Never changed. |
| Scaffold rendered (copier, template `v0.4.33`) | OK — `_src_path` canonical https, `_commit: v0.4.33` |
| Canned design layer installed, `uv sync`, commit, push `run/web` | OK, first attempt |
| Base branch gated by `grimsverk-gates` | OK at 23:28:16Z (local lane's duty) |
| Preflight — `RUN_BASE=run/web .github/scripts/unattended-ready.sh --runtime` | **REFUSED, exit 2**, twice, before and after gating |
| Detector — `RUN_BASE=run/web .claude/scripts/deliver-phase.sh` | OK: `PHASE=ORACLE BASE=run/web REASON=evidence UNCITED=BL-3 BL-4 ESC-1` |
| Iterations dispatched | **0** |
| Pull requests opened by the pipeline | **0** |

## Why it stopped, exactly

```
$ RUN_BASE=run/web .github/scripts/unattended-ready.sh --runtime
unattended-ready: cannot resolve this repository — run: gh auth login
$ echo $?
2
```

The message names the wrong cause. The credential is healthy: `gh api user`
returns `GrimsVerk` and `gh api repos/GrimsVerk/grimsverk-anvil` returns the
repository. What fails is the transport. This session's egress proxy serves
GitHub REST but refuses GraphQL:

```
$ gh repo view --json nameWithOwner --jq .nameWithOwner
HTTP 403: This GraphQL query is not enabled for this session — only the pinned
set of PR-review operations is served. Use REST via `gh api repos/{owner}/{repo}/...`
instead. (https://api.github.com/graphql)
```

`gh repo view --json` is line 82 of the readiness script and the only
GraphQL call in it; every other repository read there already uses REST and
works. A second, independent defect sits behind it at line 243: the ESC-50
hosted-platform detector probes with `gh auth status`, which also reports
failure on this platform, so even with line 82 fixed the script would refuse
with "gh holds no login at all" while the login demonstrably works.

This is a NEW escape, distinct from ESC-50. ESC-50's own fix — opening pull
requests server-side through `open-pr.yml` — is sound and untouched. What
fails is the readiness check standing in front of it.

## Anomalies worth the owner's attention

- The refusal is silent about its real nature. Both messages point at
  credentials, and three earlier sessions of this test were spent chasing
  credential problems. A lane operator following either message goes hunting
  for something that is not broken.
- `pre-commit` is not installed by `uv sync`, though the scaffold ships
  `.pre-commit-config.yaml` and the documented next step is `pre-commit
  install`. Invisible on a developer machine that already has the tool.

## What remains

Everything. No oracle ruling, no plan, no feature, no acceptance run. The
canned design layer is in place on `run/web` and the detector correctly wants
`PHASE=ORACLE` with `UNCITED=BL-3 BL-4 ESC-1`, so the run is ready to proceed
the moment the readiness check can resolve this repository over REST.
