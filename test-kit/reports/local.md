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

### F6 — FIXED in v0.4.35, confirmed live

The workspace-trust warning is **gone** from round 2.2's first worker log. Round
2.1's oracle log opened with `Ignoring 2 permissions.allow entries from
.claude/settings.json: this workspace has not been trusted`; round 2.2's opens
straight into the run header with no such line, and the driver did not refuse.
The unattended worker now runs with the full tool grant the template believes it
has. **F6 closed.**

### F7 — FIXED in v0.4.35 (substantive half); a cosmetic remainder, downgraded

The missing partner is there. `.claude/scripts/spawn-worker.sh` at v0.4.35:

```
216:  "Write(docs/DESIGN.oracle.md)" "Edit(docs/DESIGN.oracle.md)"
217:  "Write(docs/oracle/**)" "Edit(docs/oracle/**)"
```

Line 217 previously had no `Edit(...)` twin, which left the oracle with no
effective grant for the directory its handoff must go in. It now has one, so the
real defect is closed.

**What remains is noise, not breakage.** The inert `Write(...)` halves are still
in the list, and the engine still rejects each one on every worker start —
verbatim, in round 2.2's log at v0.4.35:

```
Permission allow rule (--allowed-tools): Write(docs/DESIGN.oracle.md) is not matched by file
permission checks — only Edit(path) rules are. Use Edit(docs/DESIGN.oracle.md) instead
(Edit rules cover all file-editing tools).
Permission allow rule (--allowed-tools): Write(docs/oracle/**) is not matched by file
permission checks — only Edit(path) rules are. Use Edit(docs/oracle/**) instead.
```

Worth removing, for one reason beyond tidiness: these two warnings are exactly
what a genuinely missing grant looks like, so while they fire on every run they
are the camouflage a real one would hide behind — which is precisely how F7 came
to exist. **Severity downgraded to friction.**

### F9 — CLOSED by owner ruling, 2026-08-20

The owner accepts the published register values in this branch's history: no
history rewrite, no GitHub Support ticket. Their reasoning, recorded because it
is the standing policy from here: the `.pem` content never left their machine,
and paths and aliases open no doors. The tip scrub stands, and **rule 13 governs
everything from this point forward** — which this round already demonstrates
(App identity rebuilt from the register by key, and rule-13 scans of both the
full tracked tree and the setup transcript returning clean before either was
pushed).

### F8 — CLEARED, with the owner's independent proof

Beyond the two green CI runs recorded above, the owner supplied a stronger
proof than either lane could observe: **the v0.4.35 release tag both lanes
rendered from was itself minted by an Actions job that ran to completion after
the repositories went public.** The release exists, therefore Actions ran.

| 01:39:11Z | WAIT | iteration 2. PR **#4** (`docs/oracle-20260820012830--run-local`), opened by `app/autogrims`. Oracle exited 0, 1 commit. |
| 01:39:42Z | WAIT → fix | `PR #4 red (plan review ) — dispatching a fix`. Both rednesses are template defects the fix session cannot touch — F10 and F11. |

### Per-check durations, first honest reading (Part 2 rule 9, ESC-45)

With Actions working, real numbers at last. PR #4:

| Check | Result | Duration |
| --- | --- | --- |
| `open-pr` | pass | 7s |
| `checks` | pass | 9s / 10s |
| `acceptance-criteria` | pass | 7s |
| `arm-auto-merge` | pass | 7s |
| `plan` | **fail** | 7s |
| `review` | **fail** | 15s |

`arm-auto-merge` is present and passing (ESC-36) — the arming half is now
positively observed; whether it *completes* a merge still needs a green PR.
`checks` at 9–10s is the only number worth a second look, since it runs
`uv sync --locked`, ruff, ruff-format, mypy and pytest; on a scaffold with one
placeholder test and a warm uv cache that is plausible rather than the ESC-45
"skip reporting success" shape, and its log shows each step executing. Recorded,
not filed.

---

### F10 — BLOCKER: the `CODEOWNERS actually binds` check fails closed on an unreadable API, which is exactly what it promises not to do
- **Where:** `.github/workflows/ci.yml`, `plan` job, step "CODEOWNERS actually binds". Round 2.2, PR #4, and it will fail identically on every pull request in this configuration.
- **What happened:**

  ```
  codeowners: {"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/repos#list-codeowners-errors","status":"404"} unresolvable line(s) in .github/CODEOWNERS.
  {"message":"Not Found",...}gh: Not Found (HTTP 404)
  ##[error]Process completed with exit code 1.
  ```

  Read that first line closely: the count of unresolvable lines is a JSON error
  body. The step is:

  ```sh
  errs="$(gh api "repos/${GITHUB_REPOSITORY}/codeowners/errors" --jq '.errors | length' 2>/dev/null || true)"
  if   [ -z "$errs" ];   then echo "codeowners: cannot read the validation API here — not treating that as a failure."
  elif [ "$errs" = "0" ]; then echo "codeowners: resolves cleanly…"
  else                        # fail
  ```

  `gh` writes the 404 body to **stdout**; the step redirects only **stderr**.
  So `errs` is a non-empty JSON string, `[ -z "$errs" ]` is false, `"$errs" = "0"`
  is false, and control reaches the failure branch. The `-z` guard — the entire
  implementation of "an unreadable API is a note, not a block" — is unreachable
  whenever the API answers with an error document rather than nothing.

- **Why the API 404s here, and why that is a supported configuration:** the
  endpoint reads CODEOWNERS from the repository's **default branch**, and this
  repository's default branch is `main`, which by the test's design carries the
  kit and no scaffold:

  ```
  $ git ls-tree -r --name-only origin/main | grep -i codeowners
  (no output)
  ```

  This is not an exotic setup — it is the per-base-branch lane feature the
  template shipped as the ESC-46 fix (`deliver-loop.sh --base`). Any run whose
  base branch is not the default branch can hit this, and the check has no ref
  parameter to ask about the branch actually under test.

- **The template already knows the right answer, one script over.**
  `.github/scripts/unattended-ready.sh` asks the same question and gets it
  right, because it asks about the branch:

  ```
  ready    CODEOWNERS resolves cleanly (at run/local)
  ```

  So the driver's preflight is green and the required check is red, about the
  same file, at the same moment.

- **Expected:** the comment above the step in `ci.yml` states the policy
  verbatim — "It fails only on a definite answer. An unreadable API is a note,
  not a block: a check that goes red when GitHub is having a bad morning is a
  check people learn to re-run without reading." The behaviour is the opposite,
  and the message it prints is incoherent (a JSON blob where a count belongs),
  which is what makes it hard to diagnose from the check summary alone.
- **Severity: blocker.** `plan` is a required check, so no pull request can
  merge. It is also unfixable from inside the pipeline: `.github/` is off-limits
  to every agent (Part 2 rule 3, `AGENTS.md` "Gate paths are off-limits") and
  `.github/CODEOWNERS` is CODEOWNERS-owned, so the fix session the driver
  dispatched cannot resolve it by design.

### F11 — BLOCKER: the review gate's engine is not installed, so the judgment gate cannot run at all
- **Where:** `.github/workflows/review.yml` → `.github/scripts/review.sh`, round 2.2, PR #4, `review` check (required).
- **What happened:**

  ```
  Error: claude native binary not installed.

  Either postinstall did not run (--ignore-scripts, some pnpm configs)
  or the platform-native optional dependency was not downloaded
  (--omit=optional).

  Run the postinstall manually (adjust path for local vs global install):
    node node_modules/@anthropic-ai/claude-code/install.cjs

  .github/scripts/review.sh: line 374: printf: write error: Broken pipe
  ----- review agent output -----

  -------------------------------
  review: engine 'claude' exited non-zero (1) — failing closed
  ```

- **Expected:** `AGENTS.md` lists **review** as one of the four required gates,
  "an independent read-only LLM reviewing the diff against this file, both
  design documents, the plan, and the mechanical facts CI computed". The
  workflow installs the engine itself, so a fresh scaffold is expected to be
  able to run it.
- **What the template got right:** it **failed closed** — `review: engine
  'claude' exited non-zero (1) — failing closed`. A gate that cannot form a
  judgment blocks rather than waving the change through, which is the documented
  policy and the correct direction. The defect is the install, not the fallback.
- **Severity: blocker.** Second required check that cannot go green, and equally
  unfixable from inside the pipeline (`.github/` is off-limits).

**Combined effect:** two required checks are red for reasons no diff in project
space can address, so round 2.2 cannot merge anything either. Unlike F8 this is
**not** rig or billing — both are template defects in v0.4.35. The driver is
expected to reach its three-strike stop and land its evidence, exactly as it did
in round 2.1; letting it get there is a better artifact than a kill, so it is
not being interrupted.

| 01:53:58Z | WAIT | iteration 3. PR #4 still red (`plan review`); second fix session dispatched. |

### The fix session diagnosed F10 correctly and refused to route around it — recorded positively

Round 2.1's fix sessions had nothing to say about the billing outage. This
round's first fix session, working only from a read-only grant, reached F10
independently and wrote it into the run report:

> The only real fix is in `.github/workflows/`, which `AGENTS.md` puts
> off-limits to agents. It would also be self-defeating here: adding a workflow
> file to this branch takes it out of the planning-documents carve-out, and the
> 92-line diff would then fail the exempt-branch size cap — a second red for the
> same push. Filing the escape row is likewise blocked, since `docs/escapes.md`
> must land on its own pull request and one is already open against `run/local`.

It then verified the oracle's output rather than assuming it was the culprit —
"OD-1..OD-3 carry all eight fields, cite `ESC-1`/`BL-3`/`BL-4` which all exist at
the base commit, quote `docs/VISION.md` verbatim, and `R1000` sits above the
oracle offset" — and closed by stating the limits of its own evidence:

> this session's tool grant is read-only plus a fixed set of git commands, so I
> could not open the CI job log or execute the gate scripts. The diagnosis is
> elimination across all ten steps of the job plus the project's own recorded
> precedent for this exact failure — not a local re-run. Running
> `gh api repos/GrimsVerk/grimsverk-anvil/codeowners/errors` yourself will
> confirm it in one line.

Three template promises kept at once, under a gate it could not pass: it did not
weaken or route around an off-limits gate (`AGENTS.md`, "Gate paths are
off-limits"); it observed the one-pull-request-per-base rule even when that
blocked the escape filing it wanted to make; and it obeyed "Honesty about
verification" — naming exactly what it could not observe and what the owner
should run instead. **Not a finding. This is the machinery working, and it is
worth as much to the upstream report as the two defects it was defeated by.**

---

## Round 2.2 stop, 02:00Z — and the template could NOT record it

The three-strike stop fired correctly for the second round running:

```
deliver-loop: the same checks failed three times on docs/oracle-20260820012830--run-local (plan review ) — stopping (deliver.md step 5)
deliver-loop: landing this run's evidence in docs/runs/20260820T012825Z ...
deliver-loop: collect-evidence: 1 worker log(s) into docs/runs/20260820T012825Z/workers.
deliver-loop: collect-evidence: 1 review(s) into docs/runs/20260820T012825Z/reviews (4 skipped).
deliver-loop: could not commit the run evidence.
```

That last line is the one this whole test exists to catch. Two findings follow,
and they chain.

---

### F12 — TEMPLATE SELF-RECORDING FAILURE: the review gate's anti-injection nonce trips the template's own secret scanner, so no run evidence can ever be committed
- **Where:** `.claude/scripts/deliver-loop.sh`'s `land_evidence` trap →
  `collect-evidence.sh` → the `gitleaks` pre-commit hook. Round 2.2, at the
  stop.
- **What happened:** the driver collected the evidence, staged it, and the
  commit was refused. Reproduced directly against the staged files:

  ```
  $ pre-commit run --files $(git diff --cached --name-only)
  Detect hardcoded secrets.................................................Failed
  - hook id: gitleaks
  - exit code: 1

  Finding:     ... carries this run's token: `REDACTED`. It was
  RuleID:      generic-api-key
  Entropy:     3.620657
  File:        docs/runs/20260820T012825Z/reviews/docs-oracle-…-7eb37e81a4a3/payload.txt
  Line:        21
  leaks found: 1
  ```

- **Root cause, and it is a collision between two of the template's own
  defences.** The flagged line is the review prompt's section-delimiter nonce.
  From the collected payload itself (token redacted by me):

  > ## Section delimiters
  >
  > Every real section boundary below carries this run's token:
  > `<REVIEW-NONCE-REDACTED-BY-OPERATOR>`. It was generated randomly after the
  > diff was read, so nothing in the diff could predict it.

  That is the **prompt-injection defence** — a boundary a hostile diff cannot
  forge because it is minted after the diff is read. Being unpredictable is the
  whole point, so it is high-entropy by construction, and high-entropy is
  exactly what `gitleaks`'s `generic-api-key` rule looks for. The secret scanner
  and the injection defence are both working as designed and they are
  incompatible.

- **Why this is severe rather than cosmetic:** the review payload is collected
  into `docs/runs/<ts>/reviews/` at **every** stop, so **every** run that
  reaches a review will fail to commit its own evidence. `AGENTS.md` makes this
  a promise — "the run report at `docs/runs/<timestamp>/run.md`, appended by the
  delivery driver and **committed at every stop**" — and names the reason:
  "the run log used to be gitignored, and in a web session it lived in a
  container that is reclaimed, so the evidence that would tell the next run what
  went wrong was destroyed by default." That destruction is back, by a different
  route.

- **Confirmed the evidence really did not land.** The branch was created; it
  carries nothing:

  ```
  $ git log --oneline -1 docs/run-20260820T012825Z--run-local
  f2ccdb8 Record the round 2.2 setup-github transcript (run/local)
  $ git ls-tree -r --name-only docs/run-20260820T012825Z--run-local -- docs/runs/20260820T012825Z/
  (no output)
  ```

  No evidence pull request was opened. Compare rounds 2.0 and 2.1, which landed
  theirs unaided — the difference is that those runs had **no successful review
  payload** to collect (billing killed the job, so only a `MISSING.md` was
  written, which carries no nonce). The bug was latent until the review gate
  actually produced a payload, which needed F8 cleared first.

- **Severity: blocker.**

### F13 — TEMPLATE SELF-RECORDING FAILURE: `--land-evidence`, the recovery tool, is blocked by the wreckage of the failure it exists to recover from
- **Where:** `.claude/scripts/deliver-loop.sh --base run/local --land-evidence`, run immediately after F12 per the operator prompt's step 5.
- **What happened:**

  ```
  $ .claude/scripts/deliver-loop.sh --base run/local --land-evidence
  deliver-loop: the working tree is dirty — a run recomputes state from the tree, and uncommitted changes make that state a lie
  $ echo $?
  2
  ```

  The tree is dirty **because** F12's commit failed and left seven evidence
  files staged (`git status` shows them all as `A `). So the guard is correct in
  general and exactly wrong here: the one situation `--land-evidence` was built
  for is a run whose evidence commit did not complete, and that situation always
  leaves the tree dirty. The recovery path cannot run after the failure it
  recovers from.

  `deliver-loop.sh`'s own header anticipates the case — "a run killed too hard
  for its EXIT trap to fire leaves its … dead run's owner runs `--land-evidence`
  instead" — but the guard admits only a tree someone has already cleaned by
  hand, and cleaning it by hand is what destroys the evidence.

- **Severity: blocker**, and it is the more serious of the two: F12 loses one
  run's evidence, F13 means the documented rescue never works.

### What preserved the evidence instead

The ledger — the one path no gate can block. Rescued into
`test-kit/reports/round2.2-rescued-evidence/`, complete:

```
run.md
workers/oracle-20260820012830.log
reviews/index.md
reviews/docs-oracle-20260820012830--run-local-7eb37e81a4a3/{payload,reply,verdict,meta}.txt
```

Two redactions applied by me before committing, both noted in the files: the
review nonce (a single-use delimiter for a review that has already run — not a
credential, but there is no reason to publish it) and any register values, per
rule 13.

The review's own verdict is `ENGINE_ERROR` — consistent with F11, and worth
keeping: it is the first collected review payload of this test, and it exists
only because it was rescued.

**Rule 11 note on the raw log.** `test-kit/reports/local-driver-round2.2.log` is
normally the routine copy the rule exempts. Not this time: with F12 and F13 both
firing, the raw log and this rescue are the **only** surviving records of round
2.2. The exemption does not apply.

---

# SUMMARY — LOCAL lane (`run/local`), rounds 2.0 / 2.1 / 2.2 (Part 2 rule 6)

**Driver's own exit reason (round 2.2, the one that ran to a natural stop):**
`the same checks failed three times on docs/oracle-20260820012830--run-local
(plan review ) — stopping (deliver.md step 5)`. Not a budget stop, not a
PR/hour stop, not a refusal — a pattern stop, correctly fired.

**Rounds.** Three starts, all on the same lane, each ended by an owner-directed
restart except the last:

| Round | Template | Ran | Ended by |
| --- | --- | --- | --- |
| 2.0 | v0.4.32 | 12 min | owner restart to v0.4.34 (SIGTERM) |
| 2.1 | v0.4.34 | ~25 min | its own three-strike stop (billing outage, F8) |
| 2.2 | v0.4.35 | ~32 min | its own three-strike stop (F10 + F11) |

**Phases reached:** `ORACLE` and `WAIT` only. Never reached STEWARD, PLANNER,
ORCHESTRATOR, CODER, TEST-WRITER, REVIEWER or ACCEPTANCE — every round was
stopped at the first pull request by a gate that could not go green.

**Pull requests opened: 4 on this lane** (#1, #2, #3 round 2.0/2.1; #4 round
2.2). **Merged: 0.** All four authored by the App (`app/autogrims`,
`is_bot: true`), never by the owner — ESC-26/ESC-35 confirmed four times over.

**Oracle decisions written (round 2.1, the only oracle output that survived
review):** `OD-1` (ESC-1 → requirement **R1000**, 12 significant digits),
`OD-2` (**HALTED**, BL-3 `rich` vs tenet V5), `OD-3` (BL-4 currency rejected).
Round 2.2's oracle produced an equivalent set on PR #4.

**Uncertainties filed (`BL-<n>`):** none by a planner — the planner phase was
never reached. The three seeded items BL-1, BL-2 (aliases, absolute zero) were
never ruled on for the same reason.

**Criteria status:** untouched. `acceptance-criteria` passed on PR #4 in 7s with
nothing to run; no criterion has evidence, and S4 (owner) was never reached.

## Bait map — what actually fired

| Bait | Result |
| --- | --- |
| Precision gap + ESC-1 | **fired as designed** — OD-1, cites ESC-1, adds R1000, names the measurement |
| BL-3 `rich` vs V5 | **fired as designed — first live exercise of the HALT path** |
| BL-4 currency | **fired as designed** — rejected, three alternatives weighed, left in Proposed |
| BL-1 aliases, BL-2 absolute zero | **not reached** (no planner phase) |
| Three design gaps (precision, CLI syntax, batch format) | **not reached** — these are planner-filed uncertainties |
| `convert` / `convert-batch` slug collision | **not reached** |
| Strict S1/S2/S5 vs undecided precision | **not reached** |
| S4 (owner) criterion | **not reached** |

## Observation checklist (rule 9) — final state

| Item | Result |
| --- | --- |
| App authorship, never the owner | **CONFIRMED**, 4/4 pull requests |
| `arm-auto-merge` present in the check list | **CONFIRMED** (passing, 7s, PR #4) |
| Auto-merge actually completes without a human | **NOT OBSERVED** — needs a green pull request; none existed |
| Head branch disappears after merge | **NOT OBSERVED** — nothing merged |
| Per-check durations | **RECORDED** — `open-pr` 7s, `checks` 9–10s, `acceptance-criteria` 7s, `arm-auto-merge` 7s, `plan` 7s, `review` 15s. No ESC-45 "green in 1s" skip seen; `checks` at 9–10s examined and judged genuine |
| `docs/runs/<ts>/` contains report + `reviews/` + `workers/` | **FAILED — F12.** Collected, never committed. Rescued into this ledger |
| `reviews/` free of `MISSING.md` | round 2.1 had one, **correctly** (dead review job, F8) — ESC-43 working. Round 2.2 produced a real payload |
| Evidence pull request merges (ESC-40) | **FAILED — F12/F13.** Round 2.2 opened none |
| Cross-lane `update-open-prs` re-runs checks (ESC-17) | **NOT OBSERVED** — needs a merge on the other lane while mine is open |
| Budget gauge live and updating | **CONFIRMED** — 61% → 62% → 67% across three starts, model 62% → 64% → 70% |
| Contamination probe (rule 10) | **CLEAN** — no pipeline artifact referenced `test-kit/` at any point |

## Findings

| id | Severity | State |
| --- | --- | --- |
| F1 scaffold cannot make its first commit (mypy hook) | blocker | fixed upstream v0.4.32 |
| F2 no bypass available to workers for F1 | blocker | fixed upstream v0.4.32 |
| F3 `git clean -fdx` does not discard a staged render | friction | open |
| F4 setup script's transcript advice is stale when printed | docs | open |
| F5 ruleset ships an undocumented admin bypass | bug | fixed upstream v0.4.35, confirmed live |
| F6 unattended worker silently loses its tool grant | bug | fixed upstream v0.4.35, confirmed live |
| F7 oracle granted `Write(...)` the engine ignores | bug → friction | substantive half fixed v0.4.35; inert `Write(...)` entries remain |
| F8 Actions blocked by account billing | blocker | rig, not template — cleared |
| F9 register values published before rule 13 existed | bug | closed by owner ruling |
| **F10 `CODEOWNERS actually binds` fails closed on an unreadable API** | **blocker** | **OPEN** |
| **F11 review gate's engine is not installed** | **blocker** | **OPEN** |
| **F12 SELF-RECORDING FAILURE: review nonce trips gitleaks, evidence never commits** | **blocker** | **OPEN** |
| **F13 SELF-RECORDING FAILURE: `--land-evidence` blocked by the dirty tree F12 creates** | **blocker** | **OPEN** |

Positive observations recorded rather than filed: the three-strike pattern stop
(twice), evidence landing unaided under SIGTERM (twice), ESC-43's `MISSING.md`
marking a real gap, and the fix session diagnosing F10 and refusing to route
around an off-limits gate.

## State left behind

- Driver stopped; **not restarted** (rule 7).
- `run/local` working tree is **deliberately left dirty**: seven staged evidence
  files are the only on-disk copy of round 2.2's evidence. They are rescued into
  this ledger, so the tree can be cleaned with `git reset && git clean -fdx`
  whenever the owner is ready — that is left to them, not done here.
- PR #4 open against `run/local`, red on `plan` and `review`.
- `main` never touched by this lane. `run/web` never touched by this lane.

---

# ROUND 3.1 — owner-directed restart at template v0.4.36

All four of this lane's open blockers are reported fixed upstream. Mapping, as
the owner gave it:

| Ledger finding | Upstream escape | Fix as described |
| --- | --- | --- |
| **F10** CODEOWNERS check fails closed on a 404 | **ESC-57** | the CI step queries the **head SHA** with a numeric guard |
| **F11** review engine not installed | **ESC-58** | the install re-runs `install.cjs` and proves the engine with `--version` before any review |
| **F12** review nonce trips gitleaks, evidence never commits | **ESC-59** | recorded payloads and replies **redact the spent nonce**, so the scanner and the injection defence no longer deadlock |
| **F13** `--land-evidence` blocked by the dirty tree F12 creates | **ESC-60** | landing tolerates evidence-path dirt and treats only **committed** run dirs as collisions — "your exact scenario is now a test fixture" |

Also in v0.4.36, from the web lane's findings: ESC-56 (`.pr-request.json` joins
the plan carve-out) and the licensing wording. All earlier findings stand; F10
through F13 move to *fixed upstream, pending live confirmation in this round*.

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 02:0xZ | 1. Clean the tree | `git reset && git clean -fdx` on `run/local`. Safe to do because round 2.2's evidence was already rescued into this ledger — F12's staged files were the only on-disk copy, and they are preserved under `test-kit/reports/round2.2-rescued-evidence/`. |
| 02:0xZ | 2. Reset ruleset to main-only | `include` → `["~DEFAULT_BRANCH"]`. The bypass line from the F5 fix printed again, as expected. |
| 02:0xZ | 3. Clear leftovers | PR **#4** closed with a comment naming ESC-57/ESC-58 as the reason it can now be superseded. Deleted locally: `docs/oracle-2026-08-20-1`, `docs/oracle-20260820012830--run-local`, `docs/run-20260820T012825Z--run-local`, `worker/oracle-20260820012830`; and `docs/oracle-20260820012830--run-local` on the remote. **PRs #5 and #6 deliberately untouched** — they are the web lane's, and Part 2 rule 1 forbids touching the other lane's pull requests even when they are stale. |
| 02:0xZ | 4. Rebuild at v0.4.36 | `git checkout -B run/local origin/main`, unstage + clean, re-render. `_commit: v0.4.36`, `_src_path` canonical https. App identity rebuilt from the register by key; `App identity OK`. All four hooks **Passed**; 73 files, 13 486 insertions. Rule-13 scan of every tracked file: **NONE — clean**. `git push -f` → `+ f2ccdb8...7c8fbca`. |
| 02:0xZ | 5. Bounded wait for `run/web` at v0.4.36 | Started; `run/web` still reads `_commit: v0.4.35`. Polling every 3 min, 45-min bound. |

**The milestone to watch this round:** no pipeline pull request has ever merged
in either lane. Every round so far died at the first pull request — 2.0 by owner
restart, 2.1 on the billing outage, 2.2 on F10/F11. With those cleared, the
items still marked NOT OBSERVED in the summary above become reachable for the
first time: auto-merge completing without a human (ESC-36), the head branch
disappearing after a merge (ESC-21), and the cross-lane `update-open-prs`
re-run (ESC-17). Those are the readings this round exists to take.
| 02:23Z–02:26Z | 5. Bounded wait for `run/web` | 2 polls, 3 minutes. Attempt 1: `v0.4.35`. Attempt 2: **`v0.4.36`**. Same fast handshake as round 2.2 — both agents moving together keeps this well inside the 45-minute bound. |
| 02:26Z | 5. Gate both lanes | OK. `include` → `["~DEFAULT_BRANCH","refs/heads/run/local","refs/heads/run/web"]`. |
| 02:26Z | 6. Full readiness | **GREEN.** `unattended-ready: this repository can run unattended.` Tree clean at launch. |
| 02:26Z | 6. Start the driver | pid 263505, `--budget-points 20 --max-prs 30 --max-hours 12`. |

**Start conditions verified, fourth time:**

```
  THIS RUN'S BASE BRANCH: run/local
deliver-loop: budget: weekly at 69% (model 73%), allowance 20 points, window resets Aug
deliver-loop: iteration 1: phase ORACLE
deliver-loop: dispatch oracle worker (oracle-20260820022652)
```

Weekly meter across four starts: **61% → 62% → 67% → 69%** (model 62% → 64% →
70% → 73%). Still live, still moving, still well under the allowance.

## Phase transitions — round 3.1 (Part 2 rule 5)

| Time (UTC) | PHASE | Key fields |
| --- | --- | --- |
| 02:26:52Z | ORACLE | iteration 1. Worker `oracle-20260820022652`, base `run/local`. |
| 02:36:53Z | WAIT | iteration 2. PR **#8** (`docs/oracle-20260820022652--run-local`), opened by `app/autogrims`. |
| 02:37:25Z | WAIT → fix | `PR #8 red (plan ) — dispatching a fix`. One check red, not two — see below. |

### F11 — FIXED in v0.4.36 (ESC-58), confirmed live

The review gate ran and **passed**, for the first time in this test:

```
review	pass	2m0s
```

Two minutes is a plausible duration for an LLM reading a diff — contrast round
2.2's 15-second failure, which was the engine dying on startup. `review` is a
required check and it is green. **F11 closed.**

### F10 — FIXED in v0.4.36 (ESC-57), confirmed live

The `plan` job no longer fails at "CODEOWNERS actually binds". It now reaches a
later step in the same job, which is only possible if the CODEOWNERS step
passed. **F10 closed.**

### Everything else on PR #8 is green

| Check | Result | Duration |
| --- | --- | --- |
| `open-pr` | pass | 6s |
| `checks` | pass | 9s / 12s |
| `secrets` | pass | 9s / 12s |
| `template-sync` | pass | 10s |
| `acceptance-criteria` | pass | 9s |
| `arm-auto-merge` | pass | 10s |
| `review` | **pass** | **2m0s** |
| `plan` | **fail** | 4s |

Ten of eleven required checks green. One left.

---

### F14 — BLOCKER: a freshly rendered project fails its own `plan` check on its first pull request, because the template's `AGENTS.md` cites an escape id no generated project has
- **Where:** `.github/workflows/ci.yml`, `plan` job, step "Escape citations must resolve at the base commit" (`.github/scripts/escape-refs.sh`). Round 3.1, PR #8, template v0.4.36.
- **What happened:**

  ```
  AGENTS.md cites ESC-53

  A gated document may cite an escapes entry only once that entry exists on the
  default branch. The review gate reads gated documents at the BASE commit, so a
  citation to an unmerged entry is false at the only moment anything checks it —
  and it will block again on the next push, because nothing about the ordering
  changes on its own.

  Land the entry first — a one-line stub … — then cite it from here.
  ##[error]Process completed with exit code 1.
  ```

- **This is the template, not the canned bait — verified by rendering the
  template clean into a scratch directory and reading both files:**

  ```
  template's rendered docs/escapes.md ids:   (none)
  template's rendered AGENTS.md ESC citations: ESC-53
  ```

  The rendered `AGENTS.md` line is 134: "pull-request machinery a driver without
  App identity must commit, ESC-53/56". The rendered `docs/escapes.md` is an
  **empty ledger** — correctly so, since a new project has escaped nothing yet.
  So the citation dangles on **every** fresh render, with or without this test's
  canned `escapes.md` (which carries only the seeded `ESC-1`). Substituting the
  canned file changes nothing; the failure is identical either way.

- **Expected, and this is the sharp part:** `AGENTS.md` states the rule that
  fails it, about itself. From the same file: "Citations are by id, and they
  point backward only. Every `docs/escapes.md` entry carries an id … and a gated
  document cites an entry by that id alone, **only once the entry exists on the
  default branch**. This is checked, not asked for: CI resolves every `ESC-`
  citation in **this file**, both design documents, and `docs/plans/` …". The
  document naming itself as the checked file is the document that breaks the
  check. `ESC-53` is an entry in the **template repository's** ledger; the
  citation was written for a reader of the template and shipped into every
  generated project, where the id has no referent.

- **Severity: blocker**, and unfixable from inside the pipeline for three
  independent reasons: `AGENTS.md` is off-limits to every agent (Part 2 rule 3,
  and `AGENTS.md`'s own "the things that check the code's intent"); landing an
  `ESC-53` stub in `docs/escapes.md` would require its own pull request, which
  the one-PR-per-base rule forbids while PR #8 is open; and `docs/escapes.md` is
  append-only, so nothing may quietly rewrite it either.

- **Likely a v0.4.35/v0.4.36 regression:** the citation sits in the paragraph
  describing the new push-fired pull-request machinery (ESC-53) and the
  carve-out change (ESC-56) — both shipped in the last two releases. Rounds 2.0
  through 2.2 never reached this step, because the CODEOWNERS step above it
  (F10) failed first and the job stopped there. Fixing F10 is what made F14
  visible.

---

## Round 3.1 stop, 02:5xZ — the self-recording chain works end to end

```
deliver-loop: the same checks failed three times on docs/oracle-20260820022652--run-local (plan ) — stopping (deliver.md step 5)
deliver-loop: landing this run's evidence in docs/runs/20260820T022648Z ...
deliver-loop: collect-evidence: 1 worker log(s) into docs/runs/20260820T022648Z/workers.
deliver-loop: collect-evidence: 1 review(s) into docs/runs/20260820T022648Z/reviews (6 skipped).
```

**No `could not commit the run evidence`.** The working tree is clean, the
branch pushed, and evidence pull request **#10** opened by `app/autogrims`.

### F12 — FIXED in v0.4.36 (ESC-59), confirmed live

The recorded payload now carries a placeholder where the live nonce was:

```
## Section delimiters

Every real section boundary below carries this run's token: `REVIEW-NONCE-REDACTED`. It was
generated randomly after the diff was read, so nothing in the diff could predict
```

The injection defence still gets an unforgeable delimiter at review time; the
**recorded** copy carries a constant, so `gitleaks` has no high-entropy string to
flag. Both gates now hold at once. Evidence landed unaided. **F12 closed.**

### F13 — NOT exercised this round; fix remains unconfirmed

`--land-evidence` was never needed, because F12's fix meant the ordinary commit
succeeded. ESC-60 is therefore **untested by this lane** — recorded honestly
rather than marked fixed. Confirming it needs a run whose evidence commit dies
for some other reason, which is not a thing to manufacture deliberately.

### The review gate delivered a real verdict, for the first time

```
$ git show FETCH_HEAD:docs/runs/…/verdict.txt
PASS
```

The judgment gate read the oracle's rulings and passed them. Combined with the
2m0s duration, this is the first end-to-end exercise of the only load-bearing
gate that had no fixtures — payload, reply, verdict and meta all collected and
committed.

### F14 also blocks the evidence pull request

PR #10 carries the same single red check as PR #8:

| Check | Result | Duration |
| --- | --- | --- |
| `open-pr` | pass | 6s |
| `checks` | pass | 9s / 10s |
| `secrets` | pass | 6s |
| `template-sync` | pass | 12s |
| `test-the-tests` | pass | 8s |
| `acceptance-criteria` | pass | 6s |
| `arm-auto-merge` | pass | 7s |
| `plan` | **fail** | 3s |

`gh pr view 10` → `mergeable: MERGEABLE`, `mergeStateStatus: BLOCKED`. So F14
alone now blocks **both** the work pull request and the evidence pull request,
which keeps **ESC-40** (does the evidence pull request itself merge?) unobserved
for the fourth round running. It is the only thing standing between this lane
and every remaining checklist item.

## Round 3.1 close-out

- **Driver exit reason:** three-strike pattern stop on `plan`, correctly fired
  and correctly reported. Third consecutive round to stop on its own terms.
- **Phases:** ORACLE, WAIT. **Pull requests opened: 2** (#8 work, #10 evidence),
  both App-authored. **Merged: 0.**
- **Newly confirmed fixed, live:** F10 (ESC-57), F11 (ESC-58), F12 (ESC-59).
- **Still open:** F14 (blocker, new), F13 (unconfirmed), F3, F4, F7-remainder.
- **Still never observed:** a pipeline pull request merging; a head branch
  vanishing after merge (ESC-21); auto-merge completing without a human
  (ESC-36's second half); the cross-lane `update-open-prs` re-run (ESC-17); the
  evidence pull request merging (ESC-40).
- Driver **not restarted** (rule 7). Tree clean. `main` and `run/web` untouched
  by this lane.

---

# ROUND 3.2 — owner-directed restart at template v0.4.37

**F14 = ESC-61.** Per the owner: the rendered `AGENTS.md` was citing
template-ledger ids; it now names the template's ledger in words, and a render
test forbids any `ESC-<n>` id in rendered gated documents. All earlier findings
stand.

**ESC-61 verified in the render, before committing it.** No resolvable citation
survives — `grep -oE "ESC-[0-9]+" AGENTS.md` returns nothing, and the four
remaining `ESC-` mentions are all the generic placeholder form that
`escape-refs.sh` does not resolve:

```
136:because this project's `ESC-<n>` namespace is its own)
198:already landed — an `ESC-<n>` or a `BL-<n>` — so a design change can only ever
451:entry carries an id — `ESC-<n>`, the next unused integer — and a gated document
453:branch. This is checked, not asked for: CI resolves every `ESC-` citation in
```

Line 136 is the replacement for the old `ESC-53/56` citation — the same fact,
stated without borrowing an id from another repository's ledger. That is F14's
cause removed at the source rather than papered over.

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 08:04Z | Clean the tree | `git reset && git clean -fdx`. Round 3.1's evidence needed no rescue this round — it committed normally (F12 fixed) and lives on the closed PR #10's branch history plus `test-kit/reports/local-driver-round3.1.log`. |
| 08:04Z | Reset ruleset to main-only | `include` → `["~DEFAULT_BRANCH"]`. |
| 08:05Z | Close leftovers | PRs **#8** (work) and **#10** (evidence) closed, citing ESC-61 as the reason they can be superseded. Remote branches `docs/oracle-20260820022652--run-local` and `docs/run-20260820T022648Z--run-local` deleted. Web-lane PRs **#7** and **#9** left untouched (rule 1). |
| 08:05Z | Rebuild at v0.4.37 | `_commit: v0.4.37`, `_src_path` canonical https. Identity from the register by key; `App identity OK`. All four hooks **Passed**; 73 files, 13 488 insertions. Rule-13 scan: **NONE — clean**. `git push -f` → `+ 96ece73...1bd477f`. |
| 08:05Z | Bounded wait for `run/web` at v0.4.37 | Started; `run/web` reads `_commit: v0.4.36`. Polling every 3 min, 45-min bound. |

**Fifth start of this lane.** The prize is unchanged and now has a single
credible path to it: with F10, F11, F12 and F14 all fixed, PR #8's check list
last round was ten green and one red, and the red was F14. If ESC-61 holds,
this round should produce the first merge either lane has ever managed — and
with it the four readings that have never been taken: ESC-21 (branch vanishes),
ESC-36's second half (auto-merge completes unaided), ESC-40 (the evidence pull
request merges), and eventually ESC-17 (cross-lane `update-open-prs`).

**Timestamp correction.** The five rows above were first written with
placeholder times of the form `03:0xZ`, estimated rather than read from the
clock. They are corrected here from the commit record — the scaffold commit is
`1bd477f` at **2026-08-20T08:05:31Z** and the transcript commit `02e1506` at
**08:09:03Z**. Noted rather than silently amended, because these timestamps are
the spine the two lanes are compared along and an invented one is worse than no
entry. Every other time in this ledger was read from `date -u` or from command
output at the moment it was written.

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 08:05:49Z–08:08:50Z | Bounded wait resolved | 2 polls. Attempt 1: `v0.4.36`. Attempt 2: **`v0.4.37`**. |
| 08:08Z | Gate both lanes | OK. `include` → `["~DEFAULT_BRANCH","refs/heads/run/local","refs/heads/run/web"]`. |
| 08:09Z | Full readiness | **GREEN.** `unattended-ready: this repository can run unattended.` Tree clean at launch. |
| 08:09Z | Start the driver | pid 343691, `--budget-points 20 --max-prs 30 --max-hours 12`. |

**Start conditions verified, fifth time:**

```
  THIS RUN'S BASE BRANCH: run/local
deliver-loop: budget: weekly at 74% (model 82%), allowance 20 points, window resets Aug
deliver-loop: iteration 1: phase ORACLE
deliver-loop: dispatch oracle worker (oracle-20260820080937)
```

Weekly meter across five starts: **61% → 62% → 67% → 69% → 74%** (model 62% →
64% → 70% → 73% → **82%**). The model figure is climbing faster than the
weekly one and is now the tighter of the two. Worth watching: the owner noted
the window resets partway through a 12-hour run, so the probe's rollover
handling may still be exercised this round.

## Phase transitions — round 3.2 (Part 2 rule 5)

| Time (UTC) | PHASE | Key fields |
| --- | --- | --- |
| 08:09:37Z | ORACLE | iteration 1. Worker `oracle-20260820080937`, base `run/local`. |
| 08:21:57Z | WAIT | iteration 2. PR **#12** (`docs/oracle-20260820080937--run-local`). |
| 08:22:29Z | WAIT → fix | `PR #12 red (plan ) — dispatching a fix`. A *fixable* red this time — see below. |

---

## THE FIRST MERGE — and three never-observed items answered

At **08:19:05Z** the **web** lane merged PR #11
(`docs/oracle-20260820081023--run-web` → `run/web`). Not this lane's pull
request, and not touched by this lane — but the readings it produced are ones
both lanes were sent to take, and they are recorded here because this lane could
observe them from the shared repository.

### ESC-36, second half — CONFIRMED: auto-merge completes with no human

```
$ gh pr view 11 --json mergedAt,mergedBy,baseRefName,headRefName
merged 2026-08-20T08:19:05Z by app/autogrims : docs/oracle-20260820081023--run-web -> run/web
```

**Merged by `app/autogrims`** — the App. No human touched it. The arming half
was confirmed in round 3.1 (`arm-auto-merge` present and passing); this is the
completion half, and the pair is now closed.

### ESC-21 — CONFIRMED, with the path named: the branch vanishes, immediately

Four wrong theories were on record and no branch had ever been observed to
disappear. It disappeared:

```
$ git ls-remote --heads origin 'docs/oracle-20260820081023--run-web' | wc -l
0
```

And the path is not the nightly sweep. From the Auto-merge run triggered by the
merge (`32348213733`):

```
delete-merged-branch:  success   (08:19:11Z -> 08:19:17Z)
update-open-prs:       success   (08:19:11Z -> 08:19:15Z)
sweep-merged-branches: skipped
arm-auto-merge:        skipped
```

**Immediately, by the `delete-merged-branch` job, six seconds after the merge.**
`sweep-merged-branches` — the nightly backstop — was skipped and did not need to
run. That is the answer ESC-21 has been waiting for.

### ESC-17 — the job RAN; the cross-lane scenario itself has not fired yet

`update-open-prs` executed and succeeded, with `MERGED: 11` in its environment.
But this lane's PR #12 did not exist at 08:19:11Z — it was opened at 08:21:57Z,
almost three minutes later — so there was no open local pull request to update.
The job worked; the scenario rule 9 asks about ("when the OTHER lane merges
while yours is open") did not occur. **Recorded as still unobserved**, not as
confirmed.

**One thing worth flagging while looking at it.** The job's PR list is *not*
scoped to the merged pull request's base branch — `.github/workflows/auto-merge.yml:292`:

```sh
gh pr list --repo "$REPO" --state open --limit 200 \
  --json number,headRefName,headRepositoryOwner \
  --jq ".[] | select(.headRepositoryOwner.login == \"$OWNER\") | \"\(.number)\t\(.headRefName)\"" \
  > /tmp/open-prs.txt
```

Every open pull request from the same owner is selected, on any base, and each
gets `gh pr update-branch`. So the next web-lane merge that lands while a
`run/local` pull request is open **will** reach across and update it, re-running
this lane's checks. That is what makes ESC-17 observable at all — but it is also
a coupling the per-base lane isolation (ESC-46) exists to prevent, and it spends
the other lane's CI on a branch update that cannot change anything, since
`update-branch` merges a pull request's *own* base into it. Filed as F15 below,
at low severity, because it is cheap churn rather than incorrect behaviour — and
because the owner should decide whether lane isolation is meant to cover this
job.

---

### F15 — `update-open-prs` is not base-scoped, so a merge in one lane churns the other lane's pull requests
- **Where:** `.github/workflows/auto-merge.yml:292-313`, `update-open-prs` job.
- **What happened:** the job lists **all** open pull requests owned by the
  account, filtered only by `headRepositoryOwner.login`, and calls
  `gh pr update-branch` on each except the one just merged. Nothing narrows it to
  the merged pull request's base branch. Verified by reading the rendered
  workflow at v0.4.37; observed running at 08:19:11Z with `MERGED: 11`.
- **Expected:** the template's per-base isolation is explicit elsewhere —
  `deliver-loop.sh --base`, the `--run-local` / `--run-web` branch suffixes, and
  `AGENTS.md`: "pull requests into two separate base branches are two
  independent runs, and neither waits on — or touches — the other's." This job
  touches the other's.
- **Effect, honestly bounded:** harmless in outcome. `gh pr update-branch`
  merges a pull request's own base into its head, so a `run/local` pull request
  updated after a `run/web` merge gets either a no-op or an update it would have
  wanted anyway. The cost is a re-run of that lane's full check suite — on this
  repository roughly two minutes of `review` plus eight other jobs — charged to
  a merge in a lane it has nothing to do with.
- **Severity: friction.** Not blocking, and it is the mechanism that makes
  ESC-17 observable. Worth a ruling rather than a fix: if lanes are meant to be
  isolated, this needs `--base`; if the isolation is only about *waiting* and
  not about *touching*, then `AGENTS.md`'s wording is what should change.

---

### The oracle made a real mistake and the gate caught it — recorded positively

PR #12's single red check is **not** a template defect. `oracle-decisions.sh`
refused the oracle's own work:

```
oracle-decisions: 1 problem(s):
  OD-3's vision quote is 24 characters — too short to be the statement it leans
  on. Quote the whole sentence: a fragment can be read against the sense of the
  sentence it came from, and the owner reading the ledger cannot tell.

Relaxing this check to get a decision through is gate tampering.
```

Round 2.1's oracle quoted its vision statements in full; this round's oracle cut
one to a fragment. Worker variance, caught mechanically, with a message that
names the defect, the reason it matters, and the remedy. **This is also the
first red in five rounds that the pipeline can actually fix itself** — the
decision is on a branch and has not landed, so append-only does not bar
correcting it, and `docs/DESIGN.oracle.md` is inside the fix session's grant.
Watching whether the fix session takes it.

---

## THIS LANE MERGED — the pipeline is running end to end

| Time (UTC) | PHASE | Key fields |
| --- | --- | --- |
| 08:22:29Z | fix | fix session dispatched against PR #12's `plan` red |
| **08:29:39Z** | **MERGE** | **PR #12 merged by `app/autogrims`** — first merge on `run/local` |
| 08:30:22Z | **STEWARD** | iteration 3. Worker `steward-od-1` — **a phase no round has ever reached** |
| 08:34:38Z | WAIT | iteration 4. PR **#15** (`docs/oracle-plan-od-1--run-local`) |
| **08:36:11Z** | **MERGE** | **PR #15 merged by `app/autogrims`** |
| 08:36:14Z | ORACLE | iteration 5 — the loop has come round and is running normally |

### The fix session repaired the oracle's own mistake

The 24-character vision quote that `oracle-decisions.sh` refused was corrected,
and PR #12 went from one red to fully green:

| Check | Result | Duration |
| --- | --- | --- |
| `open-pr` | pass | 7s |
| `plan` | **pass** | 6s |
| `checks` | pass | 10s / 11s |
| `secrets` | pass | 9s / 10s |
| `template-sync` | pass | 12s |
| `test-the-tests` | pass | 10s |
| `acceptance-criteria` | pass | 12s |
| `review` | **pass** | **2m3s** |
| `delete-merged-branch` | pass | 4s |
| `update-open-prs` | pass | 4s |

Eleven required checks green, `review` taking two minutes of real judgment. This
is the first time in five rounds that a dispatched fix session **succeeded** —
rounds 2.1 and 2.2 dispatched fixes against a billing outage and an off-limits
gate, neither of which any diff could touch. Given a defect that was genuinely
the pipeline's own, it fixed it in seven minutes and the pull request merged.

### ESC-21 — CONFIRMED on this lane too, both merges

```
docs/oracle-20260820080937--run-local -> 0 remote ref(s)
docs/oracle-plan-od-1--run-local      -> 0 remote ref(s)
```

`delete-merged-branch` passed in 4s on PR #12. Two for two on this lane, plus
the web lane's, and the nightly sweep has never been needed.

### The merge history is exactly what the design promises

```
$ git log --oneline --first-parent -4 origin/run/local
7a3430e Merge pull request #15 from GrimsVerk/docs/oracle-plan-od-1--run-local
6a5ed14 Merge pull request #12 from GrimsVerk/docs/oracle-20260820080937--run-local
02e1506 Record the round 3.2 setup-github transcript (run/local)
1bd477f Scaffold and canned test design (run/local)
```

Merge commits, not a rebase — which is what keeps the one-line `git revert -m 1`
rollback available that `setup-github.sh` deliberately preserves by refusing
"require linear history". Two sanctioned direct commits at the base (the
scaffold and the setup transcript), then nothing but merges. That is Part 3's
closing check 3 satisfied for this lane so far.

### Observation checklist — updated

| Item | State |
| --- | --- |
| App authorship, never the owner | **CONFIRMED** — every pull request, and both merges, by `app/autogrims` |
| `arm-auto-merge` present | **CONFIRMED** |
| Auto-merge completes without a human | **CONFIRMED** — PR #12 and #15, and the web lane's #11 |
| Head branch disappears after merge | **CONFIRMED — immediately, via `delete-merged-branch`, ~4-6s** |
| Per-check durations | **RECORDED** — no ESC-45 skip-as-success seen; `review` at 2m0s/2m3s is the honest signature |
| Evidence PR merges (ESC-40) | still unobserved — needs a run that stops |
| Cross-lane `update-open-prs` (ESC-17) | job runs; scenario still not fired (see F15) |
| Budget gauge live | **CONFIRMED** — five readings, monotonic |
| Contamination probe (rule 10) | **CLEAN** — no artifact has referenced `test-kit/` |

| 08:43:47Z | ORACLE | iteration 5 result: `gh pr create for docs/oracle-20260820083614--run-local failed` |
| 08:43:50Z | ORACLE | iteration 6 — re-dispatched immediately |
| 08:49:31Z | ORACLE | iteration 6 result: same failure, next branch |
| 08:49:34Z | ORACLE | iteration 7 — re-dispatched again |

### F16 — BLOCKER: the driver loops the ORACLE phase indefinitely when a worker's branch produces no diff, spending a full model worker per turn with no stop rule to catch it
- **Where:** `.claude/scripts/deliver-loop.sh`, ORACLE phase, round 3.2 from iteration 5 onward.
- **What happened:** after the real work merged (PRs #12 and #15), every
  subsequent oracle iteration ends like this:

  ```
  pull request create failed: GraphQL: No commits between run/local and docs/oracle-20260820083614--run-local (createPullRequest)
  deliver-loop: gh pr create for docs/oracle-20260820083614--run-local failed
  deliver-loop: iteration 6: phase ORACLE
  deliver-loop: dispatch oracle worker (oracle-20260820084350)
  pull request create failed: GraphQL: No commits between run/local and docs/oracle-20260820084350--run-local (createPullRequest)
  deliver-loop: gh pr create for docs/oracle-20260820084350--run-local failed
  deliver-loop: iteration 7: phase ORACLE
  deliver-loop: dispatch oracle worker (oracle-20260820084934)
  ```

  Three iterations so far, roughly six minutes apart, each dispatching a fresh
  oracle worker. The cause is that there is nothing left to rule on: the
  oracle's three decisions landed in PR #12 and the steward's plan in PR #15, so
  a new oracle re-derives the same ledger, its branch carries no diff against
  `run/local`, and GitHub refuses the pull request.

- **The worker reports success, which is why nothing catches it:**

  ```
  WORKER_RESULT id=oracle-20260820083614 branch=worker/oracle-20260820083614 engine=claude exit=0 commits=1
  WORKER_RESULT id=oracle-20260820084350 branch=worker/oracle-20260820084350 engine=claude exit=0 commits=1
  ```

  `exit=0 commits=1` — so `spawn-worker.sh`'s exit-3 guard ("the engine exited 0
  but committed nothing") never fires. The commit exists on the *worker* branch;
  what is empty is the *lane* branch's diff against its base. Those are different
  facts, and only the second one predicts the pull request failing.

- **No stop rule covers it.** The three-strike rule that ended rounds 2.1, 2.2
  and 3.1 keys on *the same checks failing three times on one branch*. Here no
  checks ever run, because no pull request is ever created, and each iteration
  uses a **new** branch name — so the signature never repeats and the counter
  never accumulates. The `failure-signatures` buffer holds a single hash and is
  not growing.

- **Why this is the most expensive defect found so far:** it consumes the
  resource Part 2 rule 8 names as this lane's primary limit — a full oracle
  model worker every ~6 minutes, producing nothing, with `--max-hours 12` as the
  only backstop that will certainly fire. The template's own escape record
  (ESC-32) is that the weekly budget ceiling shipped broken once without anyone
  noticing; this is the shape of failure that would exhaust it unnoticed.

- **Related observation, not yet a finding:** the `budget:` line has been
  printed **once**, at start, and has not reappeared across seven iterations.
  Rule 8 asks me to "confirm the budget line updates" during the run. It has not
  updated so far. Whether the probe re-reads and only logs on change, or does not
  re-read at all, is not yet distinguishable from outside — recorded as an open
  question rather than asserted, and it decides whether `--budget-points 20`
  can stop this loop at all.

- **Severity: blocker.** The run cannot make progress and cannot stop itself.

### F16 — CONFIRMED and still running at 09:03:46Z; the budget half is now settled

The loop did not self-correct. **Five consecutive ORACLE iterations** (5, 6, 7,
8, 9) and **four** `gh pr create` failures, one every ~6 minutes:

```
- 08:49:31Z gh pr create for docs/oracle-20260820084350--run-local failed
- 08:55:21Z iteration 8: phase ORACLE
- 09:01:07Z gh pr create for docs/oracle-20260820085521--run-local failed
- 09:01:10Z iteration 9: phase ORACLE
- 09:01:10Z dispatch oracle worker (oracle-20260820090110)
```

Roughly **27 minutes and five oracle model workers** spent since the last real
merge at 08:36:11Z, producing nothing.

**The budget line: printed exactly once, ever.**

```
$ grep -c "budget:" /tmp/anvil-local-driver.log
1
$ grep "budget:" /tmp/anvil-local-driver.log
deliver-loop: budget: weekly at 74% (model 82%), allowance 20 points, window resets Aug
```

Nine iterations, one reading — taken at start and never revisited.

**And the gauge has moved enormously in the meantime.** Read directly, at
09:03Z:

```
$ .claude/scripts/budget-probe.sh
session=59 week=1 week_model=1 reset=Aug 27, 11am (Europe/Amsterdam)
```

**week=1%, week_model=1%** — against the 74%/82% the driver is still holding
from 08:09Z. The weekly window **rolled over** during this run, exactly the
event the owner flagged as likely ("your limits reset in under 10 hours while
the drivers may run 12"). So:

- The probe itself is **healthy** — it runs, exits 0, and returns a live
  reading that tracks a real reset. `budget-probe.sh` is not the defect.
- The **driver** never re-reads it. Its ceiling is computed once, at start, from
  a number that is now wrong by 73 percentage points.
- Therefore `--budget-points 20` **cannot** stop this loop, in either direction:
  it never re-evaluates, and post-reset the true usage is 1% anyway. The only
  limit that will certainly fire is `--max-hours 12`.

This settles the open question logged with F16. The rollover machinery the owner
wanted exercised **was** exercised — and the finding is that the driver did not
notice it happen.

**Part 2 rule 8 status, stated plainly:** the start banner showed a real gauge
(required, and satisfied — four times over across five rounds). The instruction
to "confirm the budget line updates during the run" is now answered: **it does
not update**. The weekly ceiling, which ESC-32 records as having shipped broken
once before, is at present a start-time check rather than a running limit.

Driver still ALIVE at 09:03:46Z, iteration 9, awaiting the owner's decision.
Raw log to this point preserved as
`test-kit/reports/local-driver-round3.2-partial.log`.

---

## Round 3.2 final: four merges, and ESC-40 answered — the evidence pull request does NOT merge

Before the stop, the loop broke out on its own and the lane merged **four**
pull requests, all by `app/autogrims`:

| PR | Head |
| --- | --- |
| #12 | `docs/oracle-20260820080937--run-local` |
| #15 | `docs/oracle-plan-od-1--run-local` |
| #19 | `docs/oracle-20260820090807--run-local` |
| #21 | `docs/oracle-plan-od-1--run-local` |

On `SIGTERM` the evidence landed cleanly and richly — **8 worker logs, 5 review
payloads** — and evidence pull request **#22** opened. No failsafe needed.

### F17 — BLOCKER: the run-evidence pull request cannot merge; it strands `BEHIND` with nothing left that would ever update it

This is the first live reading of **ESC-40**, and it is negative.

- **All eleven required checks pass**, including `review` at 1m42s of real
  judgment and `arm-auto-merge` at 5s.
- **Auto-merge is armed, by the App**:

  ```
  "autoMerge": {"enabledAt":"2026-08-20T09:24:31Z",
                "enabledBy":{"is_bot":true,"login":"app/autogrims"},
                "mergeMethod":"MERGE"}
  ```

- **And it will not merge**, because:

  ```
  $ gh pr view 22 --json mergeStateStatus
  gate=BEHIND
  $ gh api repos/…/rulesets/21061515 --jq '.rules[]|select(.type=="required_status_checks")|.parameters'
  {"strict_required_status_checks_policy": true}
  $ git rev-list --count origin/docs/run-20260820T080932Z--run-local..origin/run/local
  2
  ```

  The ruleset `setup-github.sh` builds requires branches to be **up to date**
  before merging. The evidence branch is cut at the stop, from a commit two
  merges old, so it is born `BEHIND`.

- **Nothing will ever fix it.** The job that updates stale branches,
  `update-open-prs`, fires only on a **merge** event. The evidence pull request
  is by construction the *last* pull request of a run — there are no further
  merges on this base, so the updater never runs again, and auto-merge waits
  forever on a condition that cannot change.

- **Expected:** `AGENTS.md` treats the run report and review payloads as the
  durable evidence an unattended run leaves behind, "committed at every stop",
  and ESC-40 asks specifically whether the evidence pull request merges. It
  does not. The evidence is *pushed* and *reviewable*, so it is not lost — but
  it never reaches the base branch on its own, and every future run's evidence
  will strand the same way.

- **One escape route exists, and it is accidental:** because `update-open-prs`
  is **not base-scoped** (F15), a merge on the **other lane** would call
  `gh pr update-branch` on this stranded pull request and unblock it. So the
  bug F15 files as needless cross-lane churn is also the only thing that could
  rescue F17. Recorded because it is the sort of coupling that makes a fix to
  one break the other.

- **Severity: blocker** for ESC-40 specifically. Everything upstream of it
  worked: the stop, the collection, the commit, the push, the pull request, the
  arming, the checks.

**Round 3.2 close-out.** Phases reached: **ORACLE, WAIT, STEWARD, fix** — the
deepest any round has gone. 4 merges. Findings added: F15 (friction), F16
(blocker, fixed upstream in v0.4.39), F17 (blocker, new). Confirmed live this
round: ESC-36 both halves, ESC-21 with its path named, ESC-59, and the budget
probe's live rollover. Raw log: `test-kit/reports/local-driver-round3.2.log`.

---

# ROUND 3.3 — restart at v0.4.39, HELD at the lane handshake

Owner's instruction: F16 fixed both halves — ESC-66 (the driver compares a
worker's branch against the base before pushing, reports "adds nothing" as its
own outcome, records the dispatched scope as processed, and stops after two
dispatches in a row that produce no pull request) and ESC-67 (the budget line is
logged every iteration: weekly, per-model, and points spent). ESC-65 fixed the
truncation that hid the rollover this lane caught live.

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 09:2xZ | Stop the round 3.2 driver | `SIGTERM`. It landed evidence first — 8 worker logs, 5 review payloads — and opened evidence PR #22. No failsafe. |
| 09:29Z | Reset ruleset to main-only | `include` → `["~DEFAULT_BRANCH"]`. |
| 09:29Z | Close round-3.2 leftovers | **Operator error — see F18.** The sweep closed PR #22 along with the stale oracle branches. |
| 09:3xZ | Rebuild at v0.4.39 | `_commit: v0.4.39`. All four hooks Passed; 73 files, 13 649 insertions. Rule-13 scan clean. `git push -f` → `+ f046f98...ee07cfa`. |
| 09:30Z–10:16Z | Bounded wait for `run/web` at v0.4.39 | **TIMEOUT.** 16 polls over 45 minutes, `run/web` read `_commit: v0.4.37` every time. |

### The web lane did not restart — it is still running round 3.2 at v0.4.37

This is not a stalled lane. It is an **active** one, on the previous release:

```
$ git log -1 --format='%cI %s' origin/run/web
2026-08-20T10:16:06Z Merge pull request #27 from GrimsVerk/docs/oracle-20260820101037--run-web
```

It merged a pull request at 10:16:06Z — eight seconds before the poll's final
attempt. So the two lanes are now on **different template releases**, which
breaks the premise the whole comparison rests on ("the two scaffolds come from
the same template release with the same answers"). Per Part 1's timeout branch I
would gate `run/local` alone and continue; the owner has asked me to hold, so
nothing has been gated and no driver has been started. Recorded and awaiting
their decision.

Poll log: `test-kit/reports/wait-logs/anvil-local-waitweb39.log`.

### F18 — OPERATOR ERROR (mine): the round-3.2 evidence pull request was closed by my own cleanup sweep
- **Where:** round 3.3 restart, step 3 ("close round-3.2 leftovers"), 09:29:52Z.
- **What happened:** I implemented the step as a loop closing **every** open pull
  request targeting `run/local`. PR **#22** — the run-evidence pull request I had
  filed F17 about two minutes earlier — was open and targeting `run/local`, so it
  was closed with the stale oracle pull requests. The owner was about to update
  its branch by hand to observe whether it would then merge (the ESC-40 reading).
- **Compounding factor, from the same drill:** step 4 force-pushed `run/local`
  from `f046f98` to `ee07cfa`. The base #22 was measured against no longer
  exists, so reopening cannot replay the experiment — the two histories are
  unrelated. That destruction came from the requested rebuild, not from the
  close, but I sequenced the two without flagging that they were in conflict.
- **What was preserved:** all of it. The evidence commit `8c77559` survived in
  the local object store and is now on GitHub twice — as
  `test-kit/reports/round3.2-evidence/` on this branch, and as its own archive
  branch `evidence/run-20260820T080932Z--run-local` (commit `cc64d96`), with the
  absolute home paths in `run.md` replaced by `<home>` per rule 13 and every
  other byte unchanged.
- **What was lost:** the *live* ESC-40 experiment. F17's conclusion does not
  depend on it — the eleven green checks, the App-armed auto-merge, `BEHIND`,
  `strict_required_status_checks_policy: true` and the two-commit gap were all
  captured before anything was closed — but "update the branch by hand and watch
  whether it then merges" cannot now be run on that pull request.
- **Lesson for the drill, worth carrying:** "close leftovers" and "the evidence
  pull request" are not the same category, and a blanket sweep cannot tell them
  apart. The evidence pull request of the round being torn down is the one thing
  in the cleanup list that may still be under active observation.
- **Severity: operator error, not a template finding.** Logged under rule 4's
  "if you are unsure whether something is a finding, it is a finding", and
  because the owner's reconstruction of this round would otherwise show a
  pull request closing itself for no reason.

---

## ⚠ COMPARISON CAVEAT — from round 3.3 the two lanes are NOT version-matched

**Owner's decision, 2026-08-20.** The web lane was mid-run at **v0.4.37** and
productive — five merges in 45 minutes, and further into the pipeline than any
lane had reached (`docs/plan-anvil-temperature--run-web`,
`docs/oracle-plan-od-7--run-web`). It runs to its own stop rather than being
torn down. The local lane goes **forward** to v0.4.41 rather than back.

So from this point:

| Lane | Template | Role |
| --- | --- | --- |
| `run/web` | **v0.4.37** | effectively a **control** — the last release before the round-3.3 fixes |
| `run/local` | **v0.4.41** | carries ESC-65, 66, 67, 68, 69, 70, 71, 72, 73 |

**This invalidates the parts of Part 3 that assume one release.** Specifically:
the scaffold diff (`git diff run/local run/web -- ':!src' ':!tests' ':!docs'
':!test-kit'`) is now expected to be **large and meaningful**, not near-empty,
and any difference between the lanes' phases, counts or artifacts is
confounded by four template releases. It is a deliberate owner decision, not a
lane deviation, and it should be read as a v0.4.37-vs-v0.4.41 comparison rather
than a local-vs-web one.

## Round 3.3 — restart at v0.4.41, `run/local` gated alone

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 10:2xZ | Re-render at v0.4.41 | `_commit: v0.4.41`. All four hooks Passed; 73 files, 13 762 insertions. Rule-13 scan: **NONE — clean**. `git push -f` → `+ ee07cfa...b9cdcd3`. |
| 10:2xZ | Gate `run/local` **alone** | TESTPLAN Part 1 step 6a-4's timeout branch, on the owner's instruction. `include` → `["~DEFAULT_BRANCH","refs/heads/run/local"]`. `run/web` deliberately **not** gated by this lane — it is mid-run under its own arrangements and gating it now would change the rules under a running lane. |
| 10:23Z | Full readiness | **GREEN.** |
| 10:23Z | Start the driver | pid 445727, `--budget-points 20 --max-prs 30 --max-hours 12`. |

### ESC-72 — CONFIRMED live: readiness now refuses to start behind an open pull request

A new line in the readiness output, which did not exist in any earlier round:

```
ready    no pull request is open against 'run/local' — the run starts on a clear base
```

This is the check the owner says would have caught what stranded the other test
bed. Here it passes because the base was cleared first — but it is now a
positive precondition rather than an unexamined assumption.

### ESC-65 — CONFIRMED live: the budget reset time is no longer truncated

Every earlier round's banner ended mid-sentence:

```
deliver-loop: budget: weekly at 74% (model 82%), allowance 20 points, window resets Aug
```

Round 3.3's does not:

```
deliver-loop: budget: weekly at 6% (model 6%), allowance 20 points, window resets Aug 27, 10:59am (Europe/Amsterdam)
```

`window resets Aug` was the truncation that hid the rollover this lane caught by
probing directly at 09:03Z. The full timestamp is now printed. It also confirms
the rollover from the other side: 74% before the reset, **6%** after.

---

## Proposed TESTPLAN amendment (from F18, at the owner's request)

For Part 1's restart drill and any future round teardown:

> **Closing leftovers and closing the run's own evidence pull request are
> different categories, and a blanket sweep cannot tell them apart.**
> When clearing a round, close stale *work* pull requests by name or branch
> prefix — never by "every open pull request on the base". The run-evidence
> pull request (`docs/run-<timestamp>--<lane>`) is the artifact the round exists
> to produce and may still be under active observation, by the owner or by an
> open checklist item. Close it only after its readings are taken, and say in
> the ledger which reading it was closed on.
>
> A corollary for the rebuild that follows: force-pushing the lane base destroys
> the base any surviving pull request was measured against. If a pull request is
> being kept for observation, take the reading **before** the rebuild, not after
> — the two steps are in conflict and the drill currently orders them the wrong
> way round.

## Phase transitions — round 3.3 (Part 2 rule 5)

| Time (UTC) | PHASE | Key fields |
| --- | --- | --- |
| 10:23:17Z | ORACLE | iteration 1. Worker `oracle-20260820102317`, base `run/local`, template v0.4.41. |

---

## Round 3.3 stopped after 5 minutes, at exit code 0, having done nothing

The whole run, verbatim:

```
deliver-loop: budget: weekly at 6% (model 6%), allowance 20 points, window resets Aug 27, 10:59am (Europe/Amsterdam)
deliver-loop: the weekly window reset mid-run (Aug 27, 10:59am (Europe/Amsterdam) -> Aug 27, 11am (Europe/Amsterdam)) — re-baselining the allowance
deliver-loop: iteration 1: phase ORACLE
deliver-loop: dispatch oracle worker (oracle-20260820102317)
deliver-loop: landing this run's evidence in docs/runs/20260820T102313Z ...
Terminated   timeout "$SESSION_TIMEOUT" "$SPAWN" --id "$id" --role "$role" ...
deliver-loop: collect-evidence: 1 worker log(s) into docs/runs/20260820T102313Z/workers.
deliver-loop: collect-evidence: 0 review(s) into docs/runs/20260820T102313Z/reviews (19 skipped).
```

The trigger is in the worker's own log — the engine died:

```
=== spawn-worker[oracle-20260820102317] engine=claude branch=worker/oracle-20260820102317 base=run/local (b16c5cb) bypass=0 ===
=== 2026-08-20T10:23:17Z ===
Permission allow rule (--allowed-tools): Write(docs/DESIGN.oracle.md) is not matched by file permission checks …
Permission allow rule (--allowed-tools): Write(docs/oracle/**) is not matched by file permission checks …
Execution error
```

Evidence landed and pull request **#29** opened, so the self-recording chain
held. What it recorded is the problem.

### F19 — the driver reads a sub-minute rounding difference as a weekly window reset and re-baselines the budget on it
- **Where:** `deliver-loop.sh` budget handling, round 3.3, three seconds into the run.
- **What happened:**

  ```
  10:23:14Z window resets Aug 27, 10:59am (Europe/Amsterdam)
  10:23:17Z the weekly window reset mid-run (Aug 27, 10:59am (Europe/Amsterdam) -> Aug 27, 11am (Europe/Amsterdam)) — re-baselining the allowance
  ```

  Those two strings name the **same instant**, three seconds apart, rendered
  either side of a minute boundary — `10:59am` and `11am`. A genuine weekly
  reset moves the boundary by **seven days**, as this lane observed for real at
  09:03Z (74% → 6%, `reset=Aug 27, 11am`). This is the gauge rounding, not a
  reset.
- **Why it matters rather than being cosmetic:** re-baselining the allowance is
  how the driver decides it has a fresh budget. A comparison that fires on a
  string difference will fire at most once a minute, every run, near a minute
  boundary — and each time it resets the accounting that `--budget-points 20` is
  supposed to enforce. F16's other half was the ceiling never being re-read;
  this is the ceiling being re-zeroed on noise. Both defeat the same limit from
  opposite directions.
- **Expected:** the reset boundary should be compared as an instant, not as a
  rendered string; ESC-65 fixed the truncation that hid this field, which is
  what made the flaw visible at all.
- **Severity: bug.** It did not cause this stop, and it is not blocking — but it
  silently disarms the lane's primary limit.

### F20 — the run stopped at **exit code 0** with no reason given, after its only worker died; the report asserts the opposite in the same breath
- **Where:** round 3.3, `docs/runs/20260820T102313Z/run.md`, landed on PR #29.
- **What happened:** the landed report, in full at its end:

  ```
  - 10:23:17Z dispatch oracle worker (oracle-20260820102317)

  Stopped 2026-08-20T10:28:24Z with exit code 0.

  See .claude/scripts/deliver-loop.sh's header for what each exit code
  means. Every stop says why; none degrades silently.
  ```

  Five minutes, one dispatched worker, that worker dead of `Execution error`,
  zero work pull requests — reported as **exit code 0**, the success code, with
  no stop line naming a rule, a limit, a pattern or a failure. The driver log
  has no `stopping (…)` line either; earlier rounds always had one
  (`stopping (deliver.md step 5)`).
- **The sentence that makes it a finding rather than a gap:** the report closes
  with "**Every stop says why; none degrades silently.**" This stop said nothing
  and degraded silently, and the claim to the contrary is inside the artifact
  that fails it. An owner reading `docs/runs/20260820T102313Z/` in the morning
  sees a clean exit and would have no reason to look further.
- **Distinct from the worker error itself.** A worker engine failing is
  ordinary; `spawn-worker.sh` has exit codes for it and the driver is entitled to
  stop. What is wrong is reporting that stop as success and giving no cause. A
  non-zero exit with "the oracle worker's engine failed" would have been correct
  behaviour on the same facts.
- **Severity: blocker** for unattended trust specifically — this is the exact
  failure mode the run report exists to prevent, and it is the one an owner is
  least likely to catch, because nothing looks wrong.

### F7 — still present at v0.4.41

The two inert `Write(...)` grants still emit their rejection warnings on every
worker start, unchanged since round 2.0. Still friction, still worth removing:
in this round's log they are the two lines immediately above `Execution error`,
which is precisely the camouflage problem F7 described.

**Driver not restarted** (rule 7). Raw log:
`test-kit/reports/local-driver-round3.3.log`. Evidence pull request #29 open;
left alone this time, per the F18 amendment — its readings have not been taken.

---

## ESC-40 — CONFIRMED POSITIVE. The run-evidence pull request merged itself.

**The last never-observed item on the checklist, and the reading is good.**
Taken at 11:07Z, before anything touched the base, per the owner's step 1.

```
$ gh pr view 29 --json state,mergedAt,mergedBy,mergeCommit
state   = MERGED
merged  = 2026-08-20T10:29:52Z
by      = app/autogrims
commit  = 16532006
```

**It closed itself on its own reading — there was nothing left for me to close.**
The owner's instruction was to record which reading I closed #29 on, then close
it and delete its branch. Neither was needed: it merged unaided **88 seconds
after the driver opened it**, and `delete-merged-branch` had already removed the
branch (`git ls-remote … | wc -l` → `0`). No open pull requests remain on this
base. Said plainly rather than reported as done, because "I closed it" and "it
merged itself" are very different facts about the template.

Verified in the base branch's own history:

```
$ git log --oneline --first-parent -2 origin/run/local
1653200 Merge pull request #29 from GrimsVerk/docs/run-20260820T102313Z--run-local
b9cdcd3 Scaffold and canned test design (run/local)
```

All eleven checks green, `review` at 1m13s, `open-pr` 4s, `delete-merged-branch`
4s, `update-open-prs` 5s.

### F17 — FIXED in v0.4.41 (ESC-70), confirmed by this merge

F17 was: the evidence branch is cut from a local checkout several merges old, so
strict-up-to-date makes it **born `BEHIND`**, and `update-open-prs` can only fire
on a merge that never comes for a run's last pull request — deadlock. Under
ESC-70 the branch is cut from the freshly fetched remote tip:

```
base ahead of evidence branch by: 0 commits
```

Zero, not two. Never `BEHIND`, so auto-merge completed it in 88 seconds with no
human, no branch update, and no rescue from the cross-lane churn of F15.
**F17 closed.**

### A methodology note that cost me a stale reading

My first attempt at these readings ran
`git fetch -q origin run/local docs/run-20260820T102313Z--run-local`. The second
ref no longer existed — already deleted by `delete-merged-branch` — so the fetch
aborted with `fatal: couldn't find remote ref` **and did not update `run/local`
either**. I then read a stale `origin/run/local` that still pointed at `b9cdcd3`
and briefly concluded the merge had not landed. Corrected with
`git fetch --prune origin` before recording anything. Noted because the same
trap will catch anyone verifying ESC-21 and ESC-40 together: the very success of
ESC-21 (the branch vanishing) is what breaks the fetch you were going to use to
check ESC-40.

### F18's lesson is now in the kit

`main` at `84bf572` carries the amended wiping drill, in the plan's own words
and credited `(anvil local F18)`:

> **Order matters, and the obvious order is wrong (anvil local F18).** …
> Never close "every open pull request on the base". And take every reading
> **before** the rebuild: force-pushing the lane base destroys the base any
> surviving pull request was measured against, so a reading taken afterwards is
> a reading of something else.

Following it here is what produced the ESC-40 reading above: had I swept first,
as in round 3.3, the merge would still have happened but the evidence for it
would have been destroyed with the base.

---

# ROUND 3.4 — v0.4.42

Owner's mapping: F19 → **ESC-74** (reset boundary compared as an instant, only a
real move >1h re-baselines), F20 → **ESC-75** (every deliberate stop goes through
`stop <code> <reason>`; a stop with no reason is **exit 7 — WITHOUT REACHING A
DOCUMENTED STOP**, never 0; TERM/INT/HUP trapped and named; a failed dispatch
records engine death vs session timeout), F7 → **ESC-77** (inert `Write()`
grants removed), and mobo's F24 → **ESC-76** (readiness refuses on leftover
worktrees).

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 11:07Z | 1. Readings on PR #29 **first** | Taken before any rebuild, per the amended drill. **It had already merged itself** — see the ESC-40 section above. Nothing to close, branch already gone, no open pull requests on the base. |
| 11:09Z | 2. Update the lane to v0.4.42 | Rebuilt from `origin/main` and re-rendered. **`.copier-answers.yml` records `_commit: v0.4.42`**, `_src_path` canonical https. Read "update" as a rebuild, on the strength of step 1's phrase "before anything rebuilds the base". All four hooks Passed; 73 files, 13 897 insertions. Rule-13 scan: **NONE — clean**. `git push -f` → `+ 1653200...dac5b28`. |
| 11:10Z | 3. Readiness | **GREEN**, and both requested lines print — quoted in full below. |
| 11:10Z | 4. Start the driver | pid 474371, `--budget-points 20 --max-prs 30 --max-hours 12`. |

### Step 3, answered explicitly

Both lines are present and both are `ready`:

```
ready    no pull request is open against 'run/local' — the run starts on a clear base
ready    no leftover worktrees — no dead run's debris in the way
```

**ESC-76 confirmed present** (the leftover-worktree refusal, from mobo's F24) and
**ESC-72 confirmed present** (the open-pull-request refusal). Both pass here
because the base was cleared first; they are now stated preconditions rather
than assumptions.

### ESC-77 — CONFIRMED, at the source and pending in the logs

```
$ grep -c 'Write(docs/' .claude/scripts/spawn-worker.sh
0
```

The two inert grants are gone from the rendered scaffold. **F7 closed at
source**; step 5(c) is to confirm the warnings are absent from an actual worker
log this round.

### ESC-67 — CONFIRMED live: the budget line is now per-iteration and names the spend

A second budget line appears that has never existed before:

```
deliver-loop: budget: weekly at 10% (model 9%), allowance 20 points, window resets Aug 27, 11am (Europe/Amsterdam)
deliver-loop: budget: weekly at 10% (model 9%), spent 0 of 20 points on the per-model weekly limit
```

`spent 0 of 20 points on the per-model weekly limit` is the accounting F16's
second half showed was missing — the ceiling is now a running total, not a
start-time snapshot.

### ESC-74 — first reading good

The banner reports `window resets Aug 27, 11am (Europe/Amsterdam)` and **no**
`weekly window reset mid-run` line appeared, on the same boundary that produced
the spurious re-baseline in round 3.3. Watching every iteration for the rest of
the run, per step 5(a).

## Phase transitions — round 3.4 (Part 2 rule 5)

| Time (UTC) | PHASE | Key fields |
| --- | --- | --- |
| 11:10:19Z | ORACLE | iteration 1. Worker `oracle-20260820111019`, base `run/local`, template v0.4.42. |
