# Unattended run report — web frontend, round 3

- Run id: `20260820T013038Z`
- Started: 2026-08-20T01:30:38Z
- Stopped: 2026-08-20T01:50Z
- Frontend: `/deliver-loop` web mode, template **v0.4.35**
- **THIS RUN'S BASE BRANCH: `run/web`** — every pull request this run opened
  merges into it, and this run waited only on pull requests targeting it.
- Limits set by the owner: 30 pull requests, 12 wall-clock hours, 60
  iterations. Used: **1 pull request, ~20 minutes, 1 iteration.** No limit was
  approached; the run stopped on a blocked required check.
- Budget: no usage gauge is reachable in a web session, by design (ESC-50); the
  countable limits above stood in for it.
- Stop reason: **a required check is red for a reason inside the gate itself,
  and the fix is in a CODEOWNERS-owned path this run may not touch.**

## What ran

| # | Phase | Outcome |
| --- | --- | --- |
| 1 | ORACLE | Dispatched one oracle worker (`--role oracle --engine claude --base run/web`). Ran 7m27s, exit 0, 1 commit. Output: `docs/DESIGN.oracle.md` +55, `docs/oracle/handoff-2026-08-20-1.md` +42. |
| 1 | open | Branch pushed, `open-pr.yml` fired on the push, **PR #5 opened by `autogrims[bot]` — the App.** |
| 1 | WAIT | `plan` red, `review` red. Run stopped. |

Setup preceding the run: scaffold rendered at `_commit: v0.4.35`, canned design
layer installed, `uv sync` clean, `unattended-ready.sh --runtime` GREEN after
the base branch was gated, `coverage.sh` rc 1 (8 requirements unplanned —
normal).

## What the oracle produced

Three rulings, each citing logged evidence, all landed on PR #5:

- **OD-1** (evidence ESC-1) adds **R1000**: every printed value formats with
  `format(value, '.12g')`, so `anvil 0.1 km m` prints `100`, never
  `100.00000000000001`. It names the vision statement it relied on (V1) and the
  one that tells against it (V6), argues the latter down, rejects four
  alternatives with reasons, and adds the measurement the ratchet requires —
  blind tests on the exact printed string plus a fixed case in `acceptance/S1.sh`.
- **OD-2** (evidence BL-4) declines currency conversion. Cites V3, R8 and §3's
  non-goal, refuses to let a Proposed backlog item overrule the owner's design
  document, and names the two owner-landed edits that would change the answer.
- **OD-3** (evidence BL-3) **HALTS**: BL-3 names the `rich` dependency, tenet V5
  forbids any runtime dependency, and the two cannot both be honoured. It
  records what a decision would have said and what the owner must change in
  either direction.

## Why the run stopped

**The `plan` check fails at its final step, `CODEOWNERS actually binds`, for a
reason unrelated to this pull request.** Every planning script passed. The step
asks GitHub to validate CODEOWNERS with no `?ref=`, so it validates the default
branch — which in this repository carries no `.github/` — and gets a 404. `gh`
prints an API error body on **stdout**, so `2>/dev/null` does not suppress it and
the 404 JSON lands in the variable the step then compares against `"0"`. The
designed "cannot read the API = note, not a block" branch can never fire.

CODEOWNERS itself is clean: `gh api ".../codeowners/errors?ref=run/web"` returns
`{"errors":[]}`.

Both defects were already found and fixed once, as **ESC-48**, in
`.github/scripts/unattended-ready.sh` — whose comment names them exactly and
whose code requires the count to match `^[0-9]+$`. The fix was never propagated
to the required CI check. `run/local`'s oracle pull request shows the same
`plan failure`, so this stops both lanes.

Fixing it means editing `.github/workflows/ci.yml`, which is CODEOWNERS-owned
and off-limits to this run. So the run stops and reports, which is the correct
outcome rather than a workaround.

## Anomalies worth the owner's attention

- **A web session cannot read CI job logs or download artifacts.** Both resolve
  to Azure blob storage, which this platform's proxy refuses. The cause above
  was found only by reading the workflow file and emulating the step locally.
- **The review gate's evidence is unreachable from this lane for the same
  reason.** `collect-evidence.sh` wrote `MISSING.md` for both review runs while
  the artifact is present and healthy (32,090 bytes, not expired). The marker's
  three stated causes — expired, never uploaded, job died — are all wrong here;
  the real one is that the collecting session cannot reach the download host.
- **The `.pr-request.json` marker breaks the `plan` check's planning-path
  exemption.** The oracle branch is 97 exempt lines plus that one root file, so
  the 50-line cap applied and the check failed. Removing the marker after the
  pull request existed restored the exemption. It is not in
  `plan-resolve.sh`'s carve-out list.
- The `review` check failed at its "Headless review" step. Whether that is an
  honest rejection or an engine failure cannot be determined from this session,
  because its payload cannot be downloaded.

## What remains

The oracle's three rulings are written and open on PR #5, unmerged. No steward
plan, no milestone plan, no code, no acceptance run. The moment `plan` can pass,
the run resumes from `PHASE=ORACLE` cleanly.
