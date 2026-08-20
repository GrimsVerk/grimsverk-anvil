# Unattended run report — web frontend, round 3.6

- Run id: `20260820T130509Z`
- Started: 2026-08-20T13:05:09Z
- Stopped: 2026-08-20T16:57Z, on the owner's instruction
- Frontend: `/deliver-loop` web mode, template **v0.4.45**
- **THIS RUN'S BASE BRANCH: `run/web`** — every pull request this run opened
  merged into it, and this run waited only on pull requests targeting it.
- Limits set by the owner: 30 pull requests, 12 wall-clock hours, 60
  iterations. **Used: 11 pull requests, 3h52m, 11 iterations.** No limit was
  approached; the run stopped because the owner said to.

## What ran

Eleven iterations, cycling ORACLE → STEWARD → PLAN, with one WAIT observed.

| # | Phase | Result | PR | Merge vs `review` |
| --- | --- | --- | --- | --- |
| 1 | ORACLE | OD-1/OD-2/OD-3 — precision from ESC-1, `rich` **HALTED** on V5, currency rejected | #43 | +2s |
| 2 | STEWARD | plan `od1-output-precision` (R1000), files BL-5 | #46 | +3s |
| 3 | ORACLE | OD-4 grants BL-5 | #48 | +2s |
| 4 | PLAN | filed BL-6, BL-7, BL-8 instead of planning | #49 | +3s |
| 5 | ORACLE | OD-5, OD-6, OD-7 — invocation syntax, output contract, MVP coverage | #50 | +3s |
| 6 | STEWARD | plan `od5-convert-cli`, 306 lines | #51 | +3s |
| 7 | ORACLE | rules BL-9 | #52 | +3s |
| 8 | STEWARD | plan `od8-nonfinite-values`, 162 lines | #53 | +4s |
| 9 | PLAN | plan `temperature-conversions` (R3), 259 lines | #54 | +3s |
| 10 | PLAN | filed BL-10 — the batch request format — instead of planning R6 | #55 | +3s |
| 11 | ORACLE | rules BL-10 and BL-11 | #56 | +3s |

**Totals: 11 pull requests opened, 11 merged, every one authored by the GitHub
App (`autogrims[bot]`), none by the owner. 8+ oracle decisions, 4 plans landed,
7 uncertainties filed and ruled (BL-5 … BL-11). No code built — the design
layer absorbed every iteration.**

## The headline: F33 did not recur

Round 3.2 ended when a pull request merged 10 seconds after its required
`review` started and 2m31s before that check reported `failure`, because the
shared ruleset had been rebuilt mid-run and `run/web` silently lost its gates.

This run, under ESC-79 and ESC-80, **every one of eleven merges followed its
`review` by 2 to 4 seconds.** Not one pull request merged with a check still
running. `arm-auto-merge` armed on all eleven and refused on none — correct,
because the base stayed gated throughout; the refusal is the thing to watch for
on a lane whose gates go missing, and recording that it never fired is what
makes it meaningful when it does.

## The sweep at the stop (ESC-78)

```
sweep-branches: 0 merged branch(es) deleted, 1 unmerged left alone, 0 refused.
sweep-branches: left alone (not merged into run/web): run/local
```

Nothing to delete, because `delete-merged-branch` had already removed every
head branch within seconds of its merge. Two things follow, and the second is
the one worth acting on:

- **`0 refused` does not mean deletion works here.** A hosted session cannot
  delete a ref at all — `git push --delete` and `DELETE /git/refs/…` both 403.
  The sweep simply never had a candidate, so its behaviour under this platform's
  refusal remains untested by this run.
- **The sweep enumerated `run/local`**, the other lane's base branch, and
  reported leaving it alone. It was right to leave it — its rule is "merged
  only" — but the candidate set is not lane-scoped, so the safety here rests on
  the merged-only test rather than on the sweep knowing whose branch that is.

## Anomalies worth the owner's attention

- **A worker killed by the account's usage limit reports only `engine exited
  1`.** The reason lives in the worker log's last line ("You've hit your session
  limit · resets 3:20pm (UTC)"). The web lane has no usage gauge by design, so a
  limit is indistinguishable from a crash without opening that log. The run
  paused 1h31m and lost nothing.
- **A stale worker branch blocked a dispatch**, and `spawn-worker.sh` refused
  loudly and cleaned up after itself rather than reusing the branch — the right
  behaviour, recorded because it is the first time this lane has seen it.
- **All 11 review payloads collected are `MISSING.md`.** The artifacts exist and
  are healthy; a hosted session cannot reach the host that serves them.
- **Ten iterations went into the design layer and none into code.** Every
  uncertainty filed was genuine and every ruling cited evidence, but the
  oracle → steward → plan cycle consumed the whole run. Four plans are landed
  and unbuilt.

## What remains

Four plans landed and unbuilt: `od1-output-precision`, `od5-convert-cli`,
`od8-nonfinite-values`, `temperature-conversions`. R6 (batch) is still
unplanned, blocked on BL-10/BL-11 which iteration 11 has just ruled on. No
acceptance pass has run, so no success criterion has recorded evidence, and S4
remains the owner's.
