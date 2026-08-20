# Delivery run 20260820T012825Z

Started 2026-08-20T01:28:25Z.
Base branch: run/local (branch suffix '--run-local').

- 01:28:27Z budget: weekly at 67% (model 70%), allowance 20 points, window resets Aug
- 01:28:30Z iteration 1: phase ORACLE
- 01:28:30Z dispatch oracle worker (oracle-20260820012830)
WORKER_RESULT id=oracle-20260820012830 branch=worker/oracle-20260820012830 worktree=<home>/code/GrimsVerk/grimsverk-anvil/.worktrees/oracle-20260820012830 engine=claude exit=0 commits=1
- 01:39:11Z iteration 2: phase WAIT
- 01:39:11Z waiting on PR #4 (docs/oracle-20260820012830--run-local) — mechanical watch, no model budget
- 01:39:42Z PR #4 red (plan review ) — dispatching a fix
- 01:39:42Z dispatch fix session
I could not make this pull request green, and the reason is worth reading before anything else: neither red check is caused by anything on the branch.

## `plan` — a bug in the check itself

The `plan` job's last step asks GitHub whether `CODEOWNERS` still resolves:

```
errs="$(gh api "repos/${GITHUB_REPOSITORY}/codeowners/errors" --jq '.errors | length' 2>/dev/null || true)"
```

That query carries no `?ref=`, so it validates the **default branch** — `main`. This repository's `main` is the test-kit; the generated project (and its `.github/CODEOWNERS`) lives only on the `run/*` lanes. I confirmed `main` has no such file, and GitHub answers that with a 404. `gh` prints an error body to *stdout* and skips the `--jq` filter, so the 404's JSON lands in `errs`, is not `0`, and the step reports it as "unresolvable lines" and exits 1.

This is a defect the project has already met once and fixed in the other place it appears: `.github/scripts/unattended-ready.sh` carries an ESC-48 comment describing exactly this failure — no `?ref=`, and an error body counted as a count — and validates both. The copy inlined in `ci.yml` never got that fix.

It fits every observation: `plan` has failed on all five pull requests here, with completely different contents, in 4–10 seconds, while every other mechanical check on this pull request passed.

**What you need to land** (`.github/workflows/ci.yml`, "CODEOWNERS actually binds") — mirror `unattended-ready.sh`: pass `?ref=$GITHUB_BASE_REF`, and refuse to treat the answer as a count unless it matches `^[0-9]+$`. The `?ref=` alone unblocks this repository; the numeric guard is the part that stops the general case, and the ratchet asks for a `docs/escapes.md` row behind it (next free id here is `ESC-2`).

## `review` — the engine, not the diff

The gate posted `ENGINE_ERROR` with an empty reply: the review model exited non-zero before saying anything. The wiring is sound — the same gate passed in 55 seconds on PR #1 a couple of hours earlier, and the OAuth secret is present. Every review since has died in 12–15 seconds, which reads as a usage or auth limit rather than a code problem. It re-runs on the next push.

## Why I pushed nothing

The only real fix is in `.github/workflows/`, which `AGENTS.md` puts off-limits to agents. It would also be self-defeating here: adding a workflow file to this branch takes it out of the planning-documents carve-out, and the 92-line diff would then fail the exempt-branch size cap — a second red for the same push. Filing the escape row is likewise blocked, since `docs/escapes.md` must land on its own pull request and one is already open against `run/local`.

The oracle's content itself is clean as far as I can check it: OD-1..OD-3 carry all eight fields, cite `ESC-1`/`BL-3`/`BL-4` which all exist at the base commit, quote `docs/VISION.md` verbatim, and `R1000` sits above the oracle offset.

One caveat on how firm that is: this session's tool grant is read-only plus a fixed set of git commands, so I could not open the CI job log or execute the gate scripts. The diagnosis is elimination across all ten steps of the job plus the project's own recorded precedent for this exact failure — not a local re-run. Running `gh api repos/GrimsVerk/grimsverk-anvil/codeowners/errors` yourself will confirm it in one line.
- 01:53:58Z iteration 3: phase WAIT
- 01:53:58Z waiting on PR #4 (docs/oracle-20260820012830--run-local) — mechanical watch, no model budget
- 01:54:00Z PR #4 red (plan review ) — dispatching a fix
- 01:54:00Z dispatch fix session
## What I found

Neither red check on PR #4 is caused by anything on that branch. I pushed nothing, and here's why.

**`plan` — the check itself is broken, on every pull request in this repo.**

The last step of the `plan` job asks GitHub whether `CODEOWNERS` still resolves:

```
errs="$(gh api "repos/${GITHUB_REPOSITORY}/codeowners/errors" --jq '.errors | length' 2>/dev/null || true)"
```

That query names no branch, so it validates the **default branch** — `main`. This repo's `main` is the test-kit; the generated project and its `.github/CODEOWNERS` live only on the `run/*` lanes (`git show origin/main:.github/CODEOWNERS` → not there). GitHub answers that with a 404, `gh` prints the error body on stdout and skips the `--jq` filter, so the 404's JSON lands in `errs`, isn't `0`, and the step reports it as unresolvable lines and exits 1.

The project has already met this defect and fixed it in the other place it appears: `.github/scripts/unattended-ready.sh` carries an ESC-48 comment describing exactly it — no `?ref=`, and an error body counted as a count — and passes both. The copy inlined in `ci.yml` never got that fix.

**`review` — the engine, not the diff.** The gate posted `ENGINE_ERROR` with an empty reply: the review model exited non-zero before saying anything, and the gate fails closed. It passed in 55s on PR #1 a few hours earlier; every one since dies in 10–15s, which reads as a usage or auth limit. It re-runs on the next push.

## Why nothing could be pushed to that branch

The fix is in `.github/workflows/ci.yml` — a gate path `AGENTS.md` puts behind your review. It's also self-defeating there: adding a workflow file to this branch takes it out of the planning-documents carve-out in `plan-resolve.sh`, and its 92 added lines then hit the 50-line cap for exempt branches. The `plan` check would go red for a new reason. No edit to `docs/oracle-20260820012830--run-local` can make it green.

## What needs to land, on its own pull request

In `ci.yml`, step "CODEOWNERS actually binds" — mirror `unattended-ready.sh`:

```bash
if ! errs="$(gh api "repos/${GITHUB_REPOSITORY}/codeowners/errors?ref=${GITHUB_BASE_REF}" \
               --jq '.errors | length' 2>/dev/null)" \
   || ! printf '%s' "$errs" | grep -qE '^[0-9]+$'; then
  errs=""
fi
```

The `?ref=` alone unblocks this repo; the numeric guard is what stops the general case. The ratchet asks for a `docs/escapes.md` row behind it — next free id here is **ESC-2** — landed first as a stub.

## On verification

I could not run the gate scripts or open the CI job logs: this session's tool grant blocks script execution and `gh run --log`. So this is not a local re-run. What it is: I read every step of the `plan` job against the branch's actual base-commit content and confirmed each passes — the branch's `docs/` prefix and planning-only diff clear `plan-resolve`, `OD-1..OD-3` carry all eight fields and quote `docs/VISION.md` verbatim, `ESC-1`/`BL-3`/`BL-4` all exist at the base, `R1000` sits above the oracle offset, and the append-only and owner-authored steps have nothing to look at. Plus the decisive one: PR #1's diff touched only `docs/runs/`, so every content-dependent step there was a no-op — and `plan` still failed, in 10 seconds. That leaves only the API step.

`gh api repos/GrimsVerk/grimsverk-anvil/codeowners/errors` from your shell will confirm it in one line.
- 02:00:21Z iteration 4: phase WAIT
- 02:00:21Z waiting on PR #4 (docs/oracle-20260820012830--run-local) — mechanical watch, no model budget
- 02:00:23Z the same checks failed three times on docs/oracle-20260820012830--run-local (plan review ) — stopping (deliver.md step 5)

Stopped 2026-08-20T02:00:23Z with exit code 3.

See .claude/scripts/deliver-loop.sh's header for what each exit code
means. Every stop says why; none degrades silently.
