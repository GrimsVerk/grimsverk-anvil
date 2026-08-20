# Findings ledger — LOCAL lane (`run/local`)

Test bed: `GrimsVerk/grimsverk-anvil`. Template under test:
`GrimsVerk/grimsverk-template` release **v0.4.31**.
Operator: local Claude Code session on the owner's machine.
Ledger branch: `chore/test-report-local` (no pull request, per Part 2 rule 4).

All times are UTC.

---

## Setup log (TESTPLAN Part 1)

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 2026-08-19 20:41Z | 1. Get the repository | OK. `git clone git@<ssh_host>:GrimsVerk/grimsverk-anvil.git` into `<repos_root>`. No friction. |
| 2026-08-19 20:43Z | 2. Confirm the template release | OK. `gh release view -R GrimsVerk/grimsverk-template --json tagName --jq .tagName` → `v0.4.31`. Meets the "v0.4.31 or newer" floor. |
| 2026-08-19 20:44Z | 3. Lane branch + copier render | OK, with one note (see N1). `git switch -c run/local origin/main`, then copier rendered 72 paths. `.copier-answers.yml` records `_commit: v0.4.31` and `_src_path: https://github.com/GrimsVerk/grimsverk-template.git` (canonical https, no token, no local path — as Part 1 step 3 requires). No overwrite prompts. |
| 2026-08-19 20:45Z | 4. Install canned inputs | OK. DESIGN.md, VISION.md, BACKLOG.md, escapes.md copied over the rendered stubs. |
| 2026-08-19 20:46Z | 5. `uv sync` | OK. Python 3.14.7, 13 packages, `uv.lock` written (75 244 bytes) so it rides in the scaffold commit per ESC-47. |
| 2026-08-19 20:47Z | 5. `pre-commit install` | OK. Hook written to `.git/hooks/pre-commit`. |
| 2026-08-19 20:48Z | 5. `git commit` | **FAILED — see F1.** The scaffold cannot make its own first commit: the mypy pre-commit hook rejects the template's own `tests/conftest.py`. Lane halted here pending the owner's ruling. |

---

## Notes (not findings)

**N1 — copier was run non-interactively.** This session has no tty, so copier
was invoked as `copier copy --defaults --data project_name=grimsverk-anvil
--data language=python --data description='…' --data auto_merge=true --data
code_owner=@GrimsVerk https://github.com/GrimsVerk/grimsverk-template.git .`
The five answers are exactly the Part 1 step 3 table; `--defaults` covers any
question the table does not name. Recorded for the lane-vs-lane scaffold diff
in Part 3, in case the web lane answered interactively.

---

## Findings

### F1 — A freshly rendered scaffold cannot make its own first commit: the mypy pre-commit hook fails on the template's own `tests/conftest.py`
- **Where:** TESTPLAN Part 1 step 5 ("Toolchain BEFORE the first commit, then commit everything"), on a clean v0.4.31 render with zero project code written.
- **What happened:**

  ```
  $ pre-commit install
  pre-commit installed at .git/hooks/pre-commit
  $ git add -A
  $ git commit -m "Scaffold and canned test design (run/local)"
  ruff check...............................................................Passed
  ruff format..............................................................Passed
  mypy.....................................................................Failed
  - hook id: mypy
  - exit code: 1

  tests/conftest.py:47: error: Untyped decorator makes function "no_network" untyped  [untyped-decorator]
  Found 1 error in 1 file (checked 3 source files)

  Detect hardcoded secrets.................................................Passed
  $ echo $?
  1
  ```

  **Root cause, confirmed by direct reproduction.** The `mirrors-mypy` hook in
  `.pre-commit-config.yaml` (rev `v2.3.0`) declares no
  `additional_dependencies`, so pytest is absent from the hook's isolated
  environment:

  ```
  $ <home>/.cache/pre-commit/repoafysa_uk/py_env-python3.14/bin/python -m pip list | grep -Ei 'mypy|pytest'
  mypy                           2.3.0
  mypy_extensions                1.1.0
  ```

  Run without the hook's default `--ignore-missing-imports`, the same mypy says
  what is really wrong:

  ```
  $ <home>/.cache/pre-commit/repoafysa_uk/py_env-python3.14/bin/mypy tests/conftest.py
  tests/conftest.py:24: error: Cannot find implementation or library stub for module named "pytest"  [import-not-found]
  tests/conftest.py:47: error: Untyped decorator makes function "no_network" untyped  [untyped-decorator]
  Found 2 errors in 1 file (checked 1 source file)
  ```

  So `import pytest` resolves to `Any`, `--ignore-missing-imports` hides that
  fact, and `strict = true` (which implies `disallow_untyped_decorators`) then
  rejects `@pytest.fixture(autouse=True)` on line 47 of the template's own file.

  The same mypy version, run in the project's real environment, passes:

  ```
  $ uv run mypy
  Success: no issues found in 3 source files
  $ uv run mypy --version
  mypy 2.3.1 (compiled: yes)
  ```

- **Expected:** `.pre-commit-config.yaml`'s own header comment promises exactly
  the opposite of what happened — "If pre-commit runs ruff 0.15 while CI runs
  whatever `uv sync` resolved, the two disagree … green locally, red in CI".
  This is that failure with the signs reversed: **green in CI, red in the
  hook**, on code the template itself shipped. TESTPLAN Part 1 step 5 gives
  `pre-commit install` then `git commit` as a straight-line sequence with no
  failure branch, so a clean render is expected to commit.
- **Severity: blocker.**

### F2 — F1 is not survivable by the pipeline: every worker commit hits the same hook, and both AGENTS.md and `.claude/settings.json` forbid the only bypass
- **Where:** consequence of F1, for `.claude/scripts/spawn-worker.sh` and every phase of `deliver-loop.sh`.
- **What happened:** three things line up so that the run cannot produce a single pull request.

  1. Workers commit with plain `git` inside a worktree —
     `.claude/scripts/spawn-worker.sh:452` (`git worktree add -b "$BRANCH" …`)
     and its allowlist at line 146 (`"Bash(git add:*)" "Bash(git commit:*)"`).
  2. A git worktree shares `.git/hooks` with the main checkout, so the hook
     fires there too. Verified directly — a throwaway worktree refused a commit
     because of the installed hook:

     ```
     $ git worktree add --detach /tmp/.../hooktest HEAD
     $ cd /tmp/.../hooktest && echo hi > probe.txt && git add probe.txt
     $ git commit -m "probe: does the pre-commit hook fire in a worktree"
     No .pre-commit-config.yaml file was found
     - To temporarily silence this, run `PRE_COMMIT_ALLOW_NO_CONFIG=1 git ...`
     $ echo $?
     1
     ```

     (That worktree was cut from `main`, which carries no config — the point is
     that the hook ran at all. A worktree cut from `run/local` finds the config
     and fails on `tests/conftest.py` instead.)

     This also contradicts `.github/workflows/ci.yml:361`, which states as fact
     that "an agent working in a fresh worktree … bypasses it entirely". It does
     not. That comment is wrong, and it is the stated reason the `secrets` job
     exists — the reasoning happens to reach a good conclusion from a false
     premise.
  3. The bypass is closed by design. `AGENTS.md` (Enforcement): "A failing gate
     is fixed, never bypassed: no `--no-verify`, no skipping or weakening checks
     to get green." `.claude/settings.json:18-19` denies
     `Bash(git commit --no-verify*)` and `Bash(git commit * --no-verify*)` for
     exactly these sessions.

  And the gate that fails is one an agent is forbidden to repair:
  `.github/CODEOWNERS:18` assigns `/.pre-commit-config.yaml` to `@GrimsVerk`,
  and Part 2 rule 3 puts it off-limits to me.
- **Expected:** a rendered project is buildable by its own pipeline out of the
  box. Instead the first commit of the first worker of the first phase fails on
  a file no worker wrote, with no sanctioned repair available to any pipeline
  role.
- **Severity: blocker.** The lane cannot reach TESTPLAN Part 1 step 6 (push)
  without a ruling from the owner.

---

## CORRECTION to F1 and F2 — fixed upstream in template v0.4.32 (ESC-49)

Ruled by the owner at 2026-08-19 21:2xZ, mid-setup. F1 and F2 were real and are
now **fixed upstream**, so they stand as findings but no longer block this lane.

- **Fix release:** grimsverk-template **v0.4.32**, published 2026-08-19T21:18:58Z,
  logged upstream as **ESC-49**.
- **The fix:** the `mirrors-mypy` hook is gone. mypy is now a `language: system`
  local hook running `uv run mypy` — the exact command and environment
  `ci.yml` uses. The rendered `.pre-commit-config.yaml` at v0.4.32 now reads:

  ```yaml
      - id: mypy
        name: mypy (uv run — the same environment CI uses)
        entry: uv run mypy
        language: system
  ```

  and its header comment names the root cause in the same terms F1 found it:
  "`import pytest` in the scaffold's own tests/conftest.py was enough, and a
  freshly rendered project could not make its FIRST commit."
- **Why not `additional_dependencies`:** the upstream comment rejects that fix
  explicitly — it "would patch today's list and re-break on every typed
  dependency the project ever adds — in a CODEOWNERS-owned file no pipeline
  role may repair at 3am." That answers F2's second half directly.
- **Owner's instruction:** do not uninstall the hook. Discard the v0.4.31
  render and re-render from the latest tag. Done — see the setup log below.
- **Verified on the re-render:** `pre-commit run --all-files` is green with the
  hook installed, and the scaffold commit succeeded with all four hooks active.

Both findings keep severity **blocker** for the release they were found in
(v0.4.31). Neither cost this lane anything beyond the re-render.

---

## Setup log, second pass (TESTPLAN Part 1 from step 3, at v0.4.32)

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 21:25Z | Discard the v0.4.31 render | OK, with one snag (F3). `git clean -fdx` alone would have kept the entire render — it was staged in the index from the failed step-5 commit. `git reset` first, then `git clean -fdx`, left the tree byte-identical to `origin/main` (only `.git` and `test-kit/`). |
| 21:26Z | 2. Confirm the template release | OK. Latest is now `v0.4.32`, published 2026-08-19T21:18:58Z. Above the v0.4.31 floor. |
| 21:27Z | 3. copier render (same 5 answers) | OK. `_commit: v0.4.32`, `_src_path: https://github.com/GrimsVerk/grimsverk-template.git`. No overwrite prompts. |
| 21:28Z | 4. Install canned inputs | OK. Same four files. |
| 21:28Z | 5. `uv sync` + `pre-commit install` | OK. Python 3.14.7, `uv.lock` written, hook installed at `.git/hooks/pre-commit`. |
| 21:29Z | 5. `git commit` (hooks ACTIVE) | **OK — F1 is gone.** ruff check / ruff format / mypy (uv run) / gitleaks all Passed. 72 paths committed. |
| 21:29Z | 5. Identity check | OK. `git log -1 --format='%an <%ae>'` → `GrimsVerk <<owner_email>>`. |
| 21:30Z | 6. `git push -u origin run/local` | OK, first attempt, no rejection. The "required status checks have not succeeded" rejection the plan warns about did NOT occur — no stale ruleset survived the wipe (confirmed at 6a-1 below, which reports the ruleset as *created*, not updated). |
| 21:30Z | 6a-1. `scripts/setup-github.sh --app` | OK. Merge settings asserted (auto-merge on, merge commits on, delete-on-merge on). Secrets left alone — `CLAUDE_CODE_OAUTH_TOKEN`, `APP_ID`, `APP_PRIVATE_KEY`, `AUTO_MERGE_TOKEN` all already set. Ruleset `grimsverk-gates` **created** with required checks: `checks secrets plan template-sync test-the-tests acceptance-criteria review`. Ran with stdin closed; it prompted for nothing. See F4 for its closing advice. |
| 21:30Z | 6a-2. App identity file | OK. `cp .claude/app-identity.example .claude/app-identity`, filled `APP_ID=<app_id>` and `APP_PRIVATE_KEY=<app_pem_path>`. Confirmed gitignored (`.gitignore:18`). `.claude/scripts/app-token.sh >/dev/null && echo "App identity OK"` → **App identity OK**. |
| 21:31Z | 6a-3. Push the lane | OK. Setup transcript committed and pushed on `run/local` *before* gating, so the direct push was still allowed. |
| 21:31Z | 6a-4. Wait for `run/web` | Started. `git ls-remote --heads origin 'run/*'` → `run/local` only. Polling every 3 min, bound 45 min (deadline 22:16Z). |

---

### F3 — TESTPLAN's discard instruction is incomplete: `git clean -fdx` does not remove a staged render
- **Where:** owner's mid-run instruction to discard the v0.4.31 render ("from your lane branch run `git clean -fdx`").
- **What happened:** the render was staged, because step 5's failed commit left it in the index (`git add -A` had succeeded; only the commit was refused). `git clean` by definition only removes UNTRACKED files, and a staged path is tracked. `git ls-files` listed all 72 rendered paths, so the clean would have removed almost nothing and the re-render would have landed on top of v0.4.31 leftovers.
- **What was run instead:** `git reset` (mixed, unstaging everything) and then `git clean -fdx`, verified with `git status --short` and `git diff --stat origin/main` — both empty, so the tree matched `main` exactly before the second copier run.
- **Expected:** a discard step that is safe after a failed commit. Any project whose first commit fails leaves exactly this state, so this is not specific to this test.
- **Severity: friction.** Caught before it did harm, but silent if unnoticed — the re-render would have been a v0.4.31/v0.4.32 hybrid with no error anywhere.

### F4 — `setup-github.sh` tells you to commit its transcript to `main`, which this test forbids and which its own ruleset then blocks
- **Where:** TESTPLAN Part 1 step 6a-1, closing output of `scripts/setup-github.sh --app`.
- **What happened:** the script writes `docs/runs/setup/setup-github-20260819T213013Z.log` into the working tree and ends with:

  ```
  setup-github: Commit it: directly on main before the gates exist, or on a docs/ branch
  setup-github: after (docs/runs/ is exempt from the plan-check size cap at any size).
  ```

  Both routes are wrong here. `main` is untouchable for the whole test (TESTPLAN Part 1 principles, Part 2 rule 1), and the script has just created the `grimsverk-gates` ruleset targeting the default branch — so by the time you read the advice, "before the gates exist" has already expired, by this script's own action. The advice is stale at the moment it is printed.
- **What was done:** committed on `run/local` directly, before gating that branch at 6a-4 — the only window in which a direct push to the lane base still succeeds.
- **Expected:** advice that names a route still open after the script runs.
- **Severity: docs.** An untracked file left in the working tree at the moment the delivery driver starts is not harmless, so this is worth fixing rather than ignoring.

---

## Setup log, continued (6a-4 onward)

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 21:32Z–22:17Z | 6a-4. First poll for `run/web` | **Expired.** 16 polls at 3-minute intervals, `git ls-remote --heads origin 'run/*'` returned `run/local` only every time. Bound reached at 22:17:30Z. **Owner-side rig friction, NOT a template finding** — see R1 below. |
| 22:17Z | 6a-4 timeout branch. Gate `run/local` alone | Ran, per the TESTPLAN's own timeout instruction ("gate `run/local` alone, record a finding, continue"). `ruleset 'grimsverk-gates': updated in place (id 21061515)`, gated branches: the default branch, plus `run/local`. The owner countermanded this a moment later, but the command had already completed. No harm: the ruleset is edited in place, so the two-lane call below simply widened it. `run/web` was never touched. |
| 23:25Z | 6a-4. `run/web` confirmed present | `git ls-remote --heads origin 'run/*'` → `run/local` **and** `run/web` (`9a1cd14`). Second poll skipped on the owner's instruction, since the branch was already there. |
| 23:26Z | 6a-4. Gate BOTH lanes in one call | OK. `scripts/setup-github.sh --app --gate-branch run/local --gate-branch run/web` → `ruleset 'grimsverk-gates': updated in place (id 21061515)`, `gated branches: the default branch, plus run/local run/web`. Required checks on all three: `checks secrets plan template-sync test-the-tests acceptance-criteria review`. |
| 23:27Z | Commit + push the setup transcripts | Pushed, but **not cleanly** — the push bypassed the ruleset rather than satisfying it. See F5. |

---

### R1 — the first 6a-4 poll expired for an owner-side rig reason (recorded, not a finding)

The 45-minute bound at 6a-4 expired because the web session had not started: a
rig failure on the owner's side, which the owner diagnosed and fixed, and
explicitly ruled **not** a template defect. Logged here because TESTPLAN Part 2
rule 4 wants every wait recorded and because the two lanes' timelines are
compared afterwards — the local lane sat idle from **22:17Z to 23:25Z**, about
68 minutes, waiting for a lane partner that could not start. The template
behaved correctly throughout: it refused the run for the one genuinely missing
item and named the exact command that would fix it.

The owner then instructed: skip the second poll (the branch was already there),
gate both lanes in one call, and do not gate `run/local` alone. Recorded so the
lane-vs-lane comparison is not read as the local lane deviating from Part 1.

---

### F5 — the gates ruleset ships with an always-on admin bypass, and `setup-github.sh` never says so
- **Where:** TESTPLAN Part 1 step 6a, `scripts/setup-github.sh`; bears directly on Part 3's closing check 3 ("Check the ruleset held: … nothing pushed straight to `main`, `run/local`, or `run/web`").
- **What happened:** a plain `git push` straight to the freshly gated `run/local` **succeeded**, and GitHub reported the violations it had waived rather than refusing:

  ```
  $ git push origin run/local
  remote: Bypassed rule violations for refs/heads/run/local:
  remote:
  remote: - Changes must be made through a pull request.
  remote:
  remote: - 7 of 7 required status checks are expected.
  remote:
  To <ssh_host>:GrimsVerk/grimsverk-anvil.git
     7cb807d..e52101d  run/local -> run/local
  $ echo $?
  0
  ```

  The ruleset the template's own script created grants it:

  ```
  $ gh api repos/GrimsVerk/grimsverk-anvil/rulesets/21061515 \
      --jq '{bypass_actors, conditions: .conditions.ref_name, enforcement}'
  {"bypass_actors":[{"actor_id":5,"actor_type":"RepositoryRole","bypass_mode":"always"}],
   "conditions":{"exclude":[],"include":["~DEFAULT_BRANCH","refs/heads/run/local","refs/heads/run/web"]},
   "enforcement":"active"}
  ```

  `RepositoryRole` 5 is the repository **admin** role, `bypass_mode: always`.
- **Expected:** `setup-github.sh`'s header documents the ruleset it builds in
  detail — "active on the default branch, deletions and force-pushes blocked,
  pull request required with 0 approvals plus Code Owners review, and the
  required status checks for this project's language" — and lists what stays
  manual and why. It never mentions granting anyone a standing bypass. A reader
  of that header would conclude the branch cannot be pushed to directly.
- **Assessed honestly:** an admin bypass is plausibly deliberate (without one the
  owner can lock themselves out of their own repository during setup), and it
  does **not** weaken the unattended run — the driver acts as the GitHub App,
  which holds Contents/Pull-requests write and no repository role, so it cannot
  use this bypass and stays fully gated. The defect is that the bypass is
  undocumented and silent-by-default, and that Part 3's closing check 3 is
  written as though direct pushes were impossible when in fact they merely
  print a line that scrolls past.
- **Severity: bug.** Not blocking. The fix is one paragraph in the script header
  plus, ideally, a line in `unattended-ready.sh` reporting who can bypass.

---

## Step 7 and driver start

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 23:27Z | 7. `RUN_BASE=run/local .github/scripts/unattended-ready.sh` | **GREEN.** `unattended-ready: this repository can run unattended.` (exit 0). All 24 items `ready`, including all 7 required checks binding on the base branch `run/local` specifically. One `note` (not a failure): the App must also be installed on the template repository or `template/` branches fail `template-sync` closed. |
| 23:27Z | Read `AGENTS.md` and `GLOSSARY.md` | Done, both, in full (485 + 307 lines). |
| 23:27Z | Start the driver | Launched: `nohup .claude/scripts/deliver-loop.sh --base run/local --budget-points 8 --max-prs 30 --max-hours 12 > /tmp/anvil-local-driver.log 2>&1 &` — pid 179897. Working tree clean at launch. |

**Both mandatory start conditions verified.**

1. Base branch announcement, verbatim:

   ```
   ════════════════════════════════════════════════════════════════════
     THIS RUN'S BASE BRANCH: run/local
     Every pull request this run opens will merge into 'run/local',
     and this run waits only on pull requests targeting 'run/local'.
     Non-default base: every branch this run pushes is suffixed '--run-local'.
   ════════════════════════════════════════════════════════════════════
   ```

   Correct lane. Note the lane branch suffix `--run-local`, the ESC-46 isolation
   fix, announced up front.

2. Budget gauge — **a real reading, not a "no gauge reachable" refusal** (Part 2
   rule 8, the primary limit of this lane):

   ```
   deliver-loop: budget: weekly at 61% (model 62%), allowance 8 points, window resets Aug
   ```

   So the weekly meter was already at 61% before this run started, against an
   allowance of 8 points. Watching whether this line updates as the run
   proceeds, and recording the exact stop message if the run ends on it.

---

## Phase transitions (Part 2 rule 5)

| Time (UTC) | PHASE | Key fields |
| --- | --- | --- |
| 23:27:25Z | ORACLE | iteration 1. Worker `oracle-20260819232725`, engine `claude`, base `run/local`, 3600s timeout. Scope handed to it: **"work the logged evidence: BL-3 BL-4 ESC-1"** — the driver picked up three of the four seeded baits by id on the first pass. |

---

## Round 2.0 stopped by owner direction at 23:39Z — what it produced first

The owner restarted the round at template v0.4.34 (ESC-51) while this driver was
in its first phase. The driver was stopped with `SIGTERM`; the lane is rebuilt
below. Round 2.0 ran **12 minutes**, reached one phase, and opened one pull
request. Everything it produced is preserved:

- raw driver log → `test-kit/reports/local-driver-round2.0.log`
- oracle worker log → `test-kit/reports/round2.0-oracle-worker.log`
- the oracle's ruling → `test-kit/reports/round2.0-oracle-ruling.md`

### The template recorded its own stop, unaided — no failsafe was needed

Recorded positively, because Part 2 rule 11 exists for the opposite case. On
`SIGTERM` the driver's `EXIT` trap fired and did the whole job by itself:

```
deliver-loop: landing this run's evidence in docs/runs/20260819T232721Z ...
deliver-loop: collect-evidence: 1 worker log(s) into docs/runs/20260819T232721Z/workers.
deliver-loop: collect-evidence: no runs of review.yml to collect.
```

`--land-evidence` was **not** used. The raw-log copy above is the routine one
rule 11 exempts, not a rescue: the template's own record survives independently
on the evidence branch. **No `TEMPLATE SELF-RECORDING FAILURE` finding arises
from this stop.**

The evidence landed as a branch and a pull request, not in the working tree —
worth noting, because `find docs/runs -type f` in the checkout shows only the
setup logs and reads at first glance like the report was never written:

```
$ git ls-tree -r --name-only docs/run-20260819T232721Z--run-local -- docs/runs/
docs/runs/20260819T232721Z/run.md
docs/runs/20260819T232721Z/workers/oracle-20260819232725.log
```

`reviews/` is absent, and correctly so — the run stopped before any review ran,
and `collect-evidence` said exactly that rather than writing an empty directory
or a `MISSING.md`. That is the ESC-43 shape behaving.

### Observation checklist — first positive readings (Part 2 rule 9)

- **App authorship (ESC-26, ESC-35): CONFIRMED.** The evidence pull request was
  opened by the App, not the owner:

  ```
  $ gh pr view 1 --json author --jq '{login:.author.login, is_bot:.author.is_bot}'
  {"login":"app/autogrims","is_bot":true}
  ```

  PR #1, `docs/run-20260819T232721Z--run-local` → `run/local`, created
  2026-08-19T23:39:40Z, four seconds after the stop. `mergeable: MERGEABLE`,
  `mergeStateStatus: BLOCKED` — blocked on its required checks, which is the
  gate working.
- **Lane isolation (ESC-46): CONFIRMED.** Every branch this run pushed carries
  the `--run-local` suffix, as the start banner promised. The web lane's own
  evidence branch (`docs/run-20260819T231559Z--run-web`) sat on the same remote
  throughout and neither run touched the other.
- **Worker commit authorship:** the oracle's *git commit* is authored
  `GrimsVerk <<owner_email>>` — the owner. Not a defect: workers commit
  locally under the machine's gitconfig, and it is the *pull request* author
  that ESC-26/ESC-35 are about. Noted so the two are not confused later.
- Branch deletion after merge, auto-merge arming, per-check durations,
  cross-lane `update-open-prs`: **not yet observable** — nothing merged in
  round 2.0. Carried forward to round 2.1.

### Bait map — three of four baits fired correctly in 12 minutes (Part 3)

The driver handed the oracle `work the logged evidence: BL-3 BL-4 ESC-1`, and
the oracle committed 96 lines to `docs/DESIGN.oracle.md` in one commit:
`Rule on ESC-1, BL-3, BL-4: precision decided, rich halted, currency rejected`.

| Bait | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Precision gap + seeded ESC-1 | oracle rules citing ESC-1, names how it is measured | **OD-1**: evidence `ESC-1`, adds **R1000** ("at most 12 significant digits"), relies on V1 quoted whole, names V3 as the statement against and says why it does not forbid | **as designed** |
| BL-3 `rich` vs tenet V5 | a HALT entry (never yet exercised) **or** explicit rejection quoting V5 | **OD-2 — HALTED**, tenet relied on V5 quoted verbatim, plus "what a decision would have said" and "what it needs from the owner" | **as designed — and this is the first live exercise of the HALT path** |
| BL-4 currency | dismissed against the design's non-goals, not re-handed to the oracle each iteration | **OD-3**: rejected, cites §3 non-goals and R8, weighs and rejects three alternatives (stdlib `urllib` fetch, bundled static rates, halting), leaves the item in Proposed where only the owner moves it | **as designed** |

The `docs/oracle/handoff-*.md` file the oracle command's step 4 requires was
**not** written. **Not attributable** — the worker was still running when the
owner-directed `SIGTERM` arrived, so it may simply never have reached step 4.
Flagged for round 2.1, where the same step runs uninterrupted.

---

### F6 — the unattended worker silently loses its tool grant: the workspace is untrusted
- **Where:** round 2.0, oracle worker log (`spawn-worker.sh`, engine `claude`).
- **What happened:** first line of the worker's own log:

  ```
  Ignoring 2 permissions.allow entries from .claude/settings.json: this workspace has not been trusted.
  Run Claude Code interactively here once and accept the trust dialog, or set
  projects["<home>/code/GrimsVerk/grimsverk-anvil"].hasTrustDialogAccepted: true in <home>/.claude.json.
  ```

- **Expected:** `.claude/settings.json` describes its allow list as "a scoped
  allowlist for /orchestrate (headless workers + git worktree management)", and
  `AGENTS.md` calls `.claude/` the delivery machinery that "holds the tool grant
  every unattended session runs under". Two entries of that grant were dropped,
  and nothing in the driver's preflight noticed: `unattended-ready.sh` checks 24
  items and workspace trust is not among them. The run proceeds with a quieter
  grant than the template believes it has.
- **Severity: bug.** It did not block round 2.0 — the oracle still committed —
  but it is exactly the "gate that quietly stopped working" shape, and it is
  invisible unless you read a worker log.

### F7 — the oracle is granted `Write(...)` permissions the engine does not honour
- **Where:** round 2.0 oracle worker log; `.claude/scripts/spawn-worker.sh:212-223`.
- **What happened:** the engine rejected two of the oracle's grants outright:

  ```
  Permission allow rule (--allowed-tools): Write(docs/DESIGN.oracle.md) is not matched by file
  permission checks — only Edit(path) rules are. Use Edit(docs/DESIGN.oracle.md) instead
  (Edit rules cover all file-editing tools).
  Permission allow rule (--allowed-tools): Write(docs/oracle/**) is not matched by file
  permission checks — only Edit(path) rules are. Use Edit(docs/oracle/**) instead.
  ```

  The allow list pairs some paths but not others:

  ```
  212:  "Write(docs/DESIGN.oracle.md)" "Edit(docs/DESIGN.oracle.md)"
  213:  "Write(docs/oracle/**)"
  218:  "Write(docs/plans/oracle/**)" "Edit(docs/plans/oracle/**)"
  223:  "Write(docs/BACKLOG.md)" "Edit(docs/BACKLOG.md)"
  ```

  Line 213 is the odd one out: `docs/oracle/**` has a `Write(...)` rule and **no
  `Edit(...)` partner**. Since only `Edit` rules bind, the oracle has *no*
  effective grant for `docs/oracle/**` — which is where its handoff file must be
  written (oracle command, step 4). The three other paths survive on their
  `Edit` twin; the `Write` halves are dead weight everywhere.
- **Expected:** the oracle can write its two sanctioned paths,
  `docs/DESIGN.oracle.md` and `docs/oracle/handoff-<date>-<n>.md`.
- **Severity: bug.** A plausible cause of the missing handoff noted above,
  though the interrupted run means that is not proven. Round 2.1 should settle
  it: if the handoff is missing again from an uninterrupted oracle phase, F7 is
  the reason.

---

# ROUND 2.1 — owner-directed restart at template v0.4.34

Owner's instruction, 2026-08-19 ~23:40Z: template **v0.4.34** is out with
**ESC-51** (all session-side GitHub reads are REST now — the web platform
refuses GraphQL). Both lanes re-render on it for a clean comparison. **All
earlier F-rows stand**; nothing below retracts them.

Note that `main` also moved (`353fa2f` → `3fb55db`, 5 commits) — the test kit
itself was revised for this round. Checked before rebuilding on it: the local
lane's Part 1 steps 5, 6, 6a and 7 are **unchanged**. The only local-lane delta
is in `test-kit/PROMPT-LOCAL.md` — `--budget-points 8` → `--budget-points 20`,
matching the owner's ruling. Everything else in that diff is web-lane (ESC-50's
server-side pull-request opener, the removed App-token bootstrap, rule 12's
rewrite) or Part 0 rig.

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 23:39Z | Stop round 2.0 | `SIGTERM` to pid 179897. Evidence landed by the template's own `EXIT` trap — see the round 2.0 section above. |
| 23:41Z | Clear round 2.0 leftovers | Necessary implication of the restart, not in the owner's list: PR #1 (evidence, round 2.0) was still **open against `run/local`**, and AGENTS.md allows only one pipeline pull request in flight per base branch — the new driver would have waited on a pull request whose base tree was about to be rewritten. Closed with a comment saying why; deleted `docs/run-20260819T232721Z--run-local` locally and on the remote, removed the oracle worktree, deleted `worker/oracle-20260819232725`. Its contents are preserved in this ledger. |
| 23:43Z | 1. Reset ruleset to main-only | OK. `scripts/setup-github.sh --app` → `updated in place (id 21061515)`; `.conditions.ref_name.include` now `["~DEFAULT_BRANCH"]`. Both lane branches ungated so they can be rewritten. |
| 23:43Z | 2. Rebuild the lane | `git fetch origin main && git checkout -B run/local origin/main`, then `git reset` + `git clean -fdx` (the F3 correction again — a bare `git clean` would have kept anything staged). Tree back to `main` exactly. **`.claude/app-identity` is gitignored and was destroyed by the clean**, as the owner warned; recreated from the example with App ID `<app_id>` and key `<app_pem_path>`, re-proved: `App identity OK`. |
| 23:44Z | 2. Re-render at v0.4.34 | OK. `_commit: v0.4.34`, `_src_path` canonical https. New file present that v0.4.32 did not have: `.github/workflows/open-pr.yml` (ESC-50's server-side pull-request opener). |
| 23:44Z | 2. Canned inputs, toolchain, commit | OK. All four pre-commit hooks **Passed** (F1 stays fixed). 73 files, 13 161 insertions. Identity `GrimsVerk <<owner_email>>`. |
| 23:44Z | 2. `git push -f origin run/local` | OK, clean force-update `e52101d...b5db1b5`. **No `Bypassed rule violations` line this time** — the branch was genuinely ungated, so nothing had to be waived. That is the F5 contrast: when the gate does not apply, the push is silent; when it does apply and is waived, GitHub says so. |
| 23:45Z | 3. Wait for the web lane at v0.4.34 | **No wait needed.** `git show origin/run/web:.copier-answers.yml` already read `_commit: v0.4.34` on the first check — the web lane re-rendered first. Bounded 45-min poll not required. |
| 23:45Z | 3. Gate BOTH lanes | OK. `.conditions.ref_name.include` → `["~DEFAULT_BRANCH","refs/heads/run/local","refs/heads/run/web"]`. Setup transcripts committed and pushed before the driver started, so the tree was clean at launch. |
| 23:45Z | 4. Full readiness check | **GREEN.** `unattended-ready: this repository can run unattended.` (exit 0). |
| 23:45Z | 4. Start the driver | pid 188057, `--budget-points 20 --max-prs 30 --max-hours 12`, logging to `/tmp/anvil-local-driver.log`. Round 2.0's log preserved as `test-kit/reports/local-driver-round2.0.log`. |

**Both mandatory start conditions verified again.**

```
  THIS RUN'S BASE BRANCH: run/local
deliver-loop: budget: weekly at 62% (model 64%), allowance 20 points, window resets Aug
deliver-loop: iteration 1: phase ORACLE
deliver-loop: dispatch oracle worker (oracle-20260819234457)
```

A real gauge reading, not a refusal. The weekly meter moved 61% → **62%**
(model 62% → 64%) across round 2.0's 12 minutes, so the probe is live rather
than reporting a constant. Allowance is now the owner's 20 points.

**Watch item for this round:** the owner's limits reset in under 10 hours while
the driver may run 12, so the budget probe's rollover handling is expected to be
exercised. Recording what it does at the reset.

## Phase transitions — round 2.1 (Part 2 rule 5)

| Time (UTC) | PHASE | Key fields |
| --- | --- | --- |
| 23:44:57Z | ORACLE | iteration 1. Worker `oracle-20260819234457`, base `run/local`. |

| 23:52:52Z | WAIT | iteration 2. `waiting on PR #2 (docs/oracle-20260819234457--run-local) — mechanical watch, no model budget`. Oracle worker exited 0 with 1 commit, and this time the driver opened the pull request itself. |
| 23:52:54Z | WAIT → fix | `PR #2 red (checks secrets ) — dispatching a fix`. The redness is **not** the code — see F8. |

### Observation checklist — round 2.1 readings so far

- **App authorship (ESC-26, ESC-35): CONFIRMED again.** PR #2 is
  `by app/autogrims (bot=true)`, head `docs/oracle-20260819234457--run-local`,
  base `run/local`. Two for two.
- **`arm-auto-merge` appears in the check list: CONFIRMED** (ESC-36) — it is
  present on PR #2. Whether it *completes* a merge is still unobserved, and
  cannot be observed while F8 stands.
- **`update-open-prs`, `delete-merged-branch`, `sweep-merged-branches`** are all
  present on the run and reporting `skipping` — correct, since nothing has
  merged.
- **Per-check durations (ESC-45): all anomalous, and diagnostically so.** Every
  required check finished in **3–4 seconds**, which is the exact "far too fast
  to have done the work" signature rule 9 asks about. Here it points at F8
  rather than at a skip reporting success — they are red, not green — but it is
  worth recording that the duration heuristic caught this immediately.

---

### F8 — BLOCKER, and NOT a template defect: GitHub Actions will not start any job on this account (billing)
- **Where:** round 2.1, PR #2, every workflow, every job.
- **What happened:** every required check goes red in 3–4 seconds. The job logs
  are empty because the jobs never ran. The reason is only visible through the
  check-run annotations API:

  ```
  $ gh api repos/GrimsVerk/grimsverk-anvil/check-runs/96265553867/annotations --jq '.[].message'
  The job was not started because recent account payments have failed or your
  spending limit needs to be increased. Please check the 'Billing & plans'
  section in your settings
  ```

  Confirmed identical on a second, unrelated job (`96265540542`, the `checks`
  job of a different workflow run), so it is account-wide, not job-specific.
  All three workflow runs triggered at 23:52:52Z — CI, Auto-merge, Review —
  report `failure` without executing anything:

  ```
  $ gh api repos/GrimsVerk/grimsverk-anvil/actions/runs \
      --jq '.workflow_runs[0:3][] | "\(.name) \(.conclusion) \(.created_at)"'
  CI failure 2026-08-19T23:52:52Z
  Auto-merge failure 2026-08-19T23:52:52Z
  Review failure 2026-08-19T23:52:52Z
  ```

- **Why this stops the lane completely.** The merge pipeline is defined by
  required checks going green (`AGENTS.md`, "The merge pipeline"). No check can
  go green while jobs cannot start, so **nothing can ever merge**: no plan, no
  code, no acceptance, no evidence pull request. Every remaining item on the
  observation checklist — branch deletion after merge, auto-merge actually
  completing, per-check durations of real runs, cross-lane `update-open-prs` —
  is unobservable until this is cleared. It blocks the **web lane** identically,
  since both lanes share the repository and the account.
- **Severity: blocker. Owner-side / rig, explicitly NOT a template finding.**
  Recorded here because Part 2 rule 4 wants every blocker recorded and because
  it explains every red check in both lanes' evidence from 23:52Z onward. The
  template behaved correctly throughout: it detected red, said which checks were
  red, and dispatched a fix — which is right for a code failure and cannot
  succeed against an infrastructure one.
- **The template question this raises, which IS worth answering upstream:** the
  driver cannot distinguish "the code is wrong" from "the runner never started",
  and its response to both is to spend model budget on a fix session. A red
  check whose annotation says the job never started is not fixable by any diff.
  Whether the driver should detect that and stop instead of paying for fix
  sessions is a genuine template design question — logged here, pending the
  owner, and deliberately not filed as a defect against v0.4.34 without their
  ruling.

---

## Round 2.1 ended on its own terms at 23:5xZ — the driver stopped itself

The owner-directed restart to v0.4.35 arrived while round 2.1 was in WAIT. A
`SIGTERM` was sent to the driver, but **it had already decided to stop before
the signal took effect**:

```
deliver-loop: iteration 4: phase WAIT
deliver-loop: PR #2 red (acceptance-criteria arm-auto-merge checks checks plan review secrets secrets template-sync test-the-tests ) — dispatching a fix
deliver-loop: dispatch fix session
deliver-loop: iteration 5: phase WAIT
deliver-loop: the same checks failed three times on docs/oracle-20260819234457--run-local (…) — stopping (deliver.md step 5)
deliver-loop: landing this run's evidence in docs/runs/20260819T234453Z ...
deliver-loop: collect-evidence: 1 worker log(s) into docs/runs/20260819T234453Z/workers.
deliver-loop: collect-evidence: 1 review(s) into docs/runs/20260819T234453Z/reviews (1 skipped).
```

**This answers the open template question left hanging in F8, in the
template's favour.** F8 asked whether the driver would spend budget forever on
fix sessions it cannot succeed at. It does not: three identical failures on one
branch and it stops, cites the rule it stopped under (`deliver.md` step 5), and
lands its evidence. Against a billing outage no diff could fix, it burned
**two** fix sessions and quit. That is the correct bounded behaviour, and the
concern logged in F8 is withdrawn — the design question it raised is answered.

**Evidence landed unaided, again — no failsafe.** `--land-evidence` was not
needed for the second time. Evidence pull request **#3**
(`docs/run-20260819T234453Z--run-local` → `run/local`), authored by
`app/autogrims`. Contents:

```
docs/runs/20260819T234453Z/run.md
docs/runs/20260819T234453Z/workers/oracle-20260819234457.log
docs/runs/20260819T234453Z/reviews/index.md
docs/runs/20260819T234453Z/reviews/docs-oracle-…-737aaf5cb40d/MISSING.md
```

**The `MISSING.md` is ESC-43 working, not failing.** Rule 9 asks for `reviews/`
payloads *with no* `MISSING.md`, so this needs saying plainly: the marker is
present because the review job never started (F8, billing), and the file exists
precisely to make that gap visible:

> The run happened; its artifact could not be downloaded (expired, never
> uploaded, or the job died before the upload step). This file exists so the
> gap is visible rather than indistinguishable from a review that never ran.

`index.md` closes with `Collected 1 review(s); 1 skipped or unavailable.` The
gate is honest about its own blind spot. **Not a finding — a positive
observation of ESC-43's mechanism under a real outage.**

Raw log preserved: `test-kit/reports/local-driver-round2.1.log`.

---

### F9 — register values were already published: this ledger carried them before rule 13 existed
- **Where:** this ledger and its log copies on `chore/test-report-local`, commits from 2026-08-19 20:4xZ onward; TESTPLAN Part 2 rule 13 (new in the v0.4.35 kit).
- **What happened:** rule 13 says "A register value found in anything pushed is
  itself a finding", so this is filed as one against myself. Every ledger entry
  before this round was written while the repository was private and the kit
  told me to take the App id and key path from my prompt. The repository is now
  public, and those commits are public with it. Counted at the moment rule 13
  landed, across `test-kit/reports/`:

  | Register key | Occurrences found |
  | --- | --- |
  | `<home>` | 6 |
  | `<owner_email>` | 3 |
  | `<app_pem_path>` | 2 |
  | `<ssh_host>` | 2 |
  | `<app_id>` | 2 |
  | `<repos_root>` | 1 |

- **What was done:** every occurrence is replaced by its `<key>` in the working
  tree and committed, so the branch **tip** is clean and verified clean
  (`grep` for each literal returns 0). All future entries use keys only.
- **What was NOT done, and needs the owner's decision:** scrubbing the tip does
  not remove the values from the branch's **history**. They remain in earlier
  commits, and on a public repository those commits stay reachable by SHA even
  after a force-push, until GitHub garbage-collects — which for a fork-network
  repository may require asking GitHub Support. Only the owner can weigh that.
  Note what is and is not exposed: the `.pem` **contents** were never written
  anywhere (only its path), and an App id is not a credential. The genuinely
  personal values are the home directory, the repos root, the SSH host alias
  and the owner's git email.
- **Expected:** the kit's own instruction chain produced this — Part 0 and the
  local prompt supplied these values directly until v0.4.35 moved them to the
  register. It is not a template defect and not a lane deviation; it is the
  cost of going public mid-test, and rule 13 is the fix.
- **Severity: bug** (rule 13 makes it a finding by definition; the exposure
  itself is low, and the remaining decision is the owner's).

---

# ROUND 2.2 — owner-directed restart at template v0.4.35

Owner's instruction, 2026-08-20 ~01:1xZ: v0.4.35 carries **F5, F6 and F7 from
this ledger**, plus the web lane's four fixes; both repositories are now
**public**; the kit gained the owner's identity register (Part 0) and **Part 2
rule 13**. All earlier findings stand. Kit re-read in full from `main`
(`09a5e4f`, 504 lines) before acting.

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 01:1xZ | Stop round 2.1 | `SIGTERM` sent, but the driver had **already stopped itself** — see the round 2.1 section. Evidence landed unaided; PR #3 opened by the App. |
| 01:2xZ | Re-read the kit | Done. Local-lane deltas: values now come from the register by key, minimum release v0.4.35, new rule 13, and Part 3 closing action 3 rewritten around F16 (the web credential is owner-grade, so "the ruleset held" is verified, never assumed). |
| 01:2xZ | 1. Reset ruleset to main-only | OK. `include` → `["~DEFAULT_BRANCH"]`. |
| 01:2xZ | 2. Clear round-2.1 leftovers | PRs **#2** ("Oracle: rulings and handoff") and **#3** (run evidence) closed with a comment; local worktrees pruned; `docs/oracle-20260819234457--run-local` and `docs/run-20260819T234453Z--run-local` deleted locally and on the remote. |
| 01:2xZ | 3. Rebuild at v0.4.35 | `git checkout -B run/local origin/main`, unstage + clean, re-render. `_commit: v0.4.35`, `_src_path` canonical https. `main` now also carries a `LICENSE` (MIT, go-public). App identity rebuilt **from the register by key** (`app_id`, `app_pem_path`) — values never echoed to the terminal or a file. `App identity OK`. |
| 01:2xZ | 3. Toolchain, commit, push -f | All four hooks **Passed**. 73 files, 13 419 insertions. Rule-13 scan of every tracked file before pushing: **NONE — clean**. `git push -f` → `+ 8ea3a52...7a26bd9`. |
| 01:24Z–01:27Z | 4. Bounded wait for `run/web` at v0.4.35 | 2 polls, 3 minutes. Attempt 1: `v0.4.34`. Attempt 2: **`v0.4.35`**. Well inside the 45-minute bound. |
| 01:28Z | 4. Gate both lanes | OK. `include` → `["~DEFAULT_BRANCH","refs/heads/run/local","refs/heads/run/web"]`. |
| 01:28Z | 5. Full readiness | **GREEN.** `unattended-ready: this repository can run unattended.` |
| 01:28Z | 5. Start the driver | pid 234053, `--budget-points 20 --max-prs 30 --max-hours 12`. |

**Start conditions verified for the third time.**

```
  THIS RUN'S BASE BRANCH: run/local
deliver-loop: budget: weekly at 67% (model 70%), allowance 20 points, window resets Aug
deliver-loop: iteration 1: phase ORACLE
deliver-loop: dispatch oracle worker (oracle-20260820012830)
```

Weekly meter across the three starts: **61% → 62% → 67%** (model 62% → 64% →
70%). The probe tracks a real, moving subscription.

---

### F8 — CLEARED at 01:2xZ

Actions billing is resolved (both repositories going public is the likely
cause). Observed directly, rather than assumed:

```
$ gh api repos/GrimsVerk/grimsverk-anvil/actions/runs \
    --jq '.workflow_runs[0:2][] | "\(.created_at) \(.name) \(.head_branch) -> \(.status)/\(.conclusion)"'
2026-08-20T01:26:05Z CI run/web -> completed/success
2026-08-20T01:24:14Z CI run/local -> completed/success
```

Jobs start and finish green on both lanes. Every observation-checklist item
that F8 made unobservable — branch deletion after merge, auto-merge completing,
per-check durations of real runs, cross-lane `update-open-prs` — is back in
play for round 2.2.

### F5 — FIXED in v0.4.35, confirmed live

The setup script now announces the bypass it grants, in its own output:

```
setup-github: ruleset bypass: repository admins, always — direct admin pushes are WAIVED, not blocked; the App and every non-admin stay fully gated.
```

That is exactly the gap F5 named. The bypass itself still exists and still
fires — pushing the setup transcript to the gated `run/local` produced
`Bypassed rule violations … 7 of 7 required status checks are expected` — but
it is now declared rather than silent, and the declaration correctly states
that the App stays gated. **F5 closed.**

### F7 — partly answered by round 2.1

Round 2.1's oracle pull request was titled **"Oracle: rulings and handoff"**,
so the handoff file *was* written under v0.4.34 despite the missing `Edit`
grant for `docs/oracle/**`. The grant gap was real (the engine said so
verbatim) but did not block the write in practice. v0.4.35 fixes the grant
regardless. Watching round 2.2's oracle phase to confirm the warning is gone.

### F6 — watch item for round 2.2

v0.4.35 is said to make the driver refuse untrusted workspaces. The round 2.2
start banner shows **no trust warning and no refusal**, which is consistent
with either "fixed and the workspace is now trusted" or "the check did not
fire". Resolving it from the first worker log of this round.

## Phase transitions — round 2.2 (Part 2 rule 5)

| Time (UTC) | PHASE | Key fields |
| --- | --- | --- |
| 01:28:30Z | ORACLE | iteration 1. Worker `oracle-20260820012830`, base `run/local`. |
