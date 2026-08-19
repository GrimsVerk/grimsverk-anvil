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
| 2026-08-19 20:41Z | 1. Get the repository | OK. `git clone git@github.com-grimsverk:GrimsVerk/grimsverk-anvil.git` into `~/code/GrimsVerk`. No friction. |
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
  $ /home/loke/.cache/pre-commit/repoafysa_uk/py_env-python3.14/bin/python -m pip list | grep -Ei 'mypy|pytest'
  mypy                           2.3.0
  mypy_extensions                1.1.0
  ```

  Run without the hook's default `--ignore-missing-imports`, the same mypy says
  what is really wrong:

  ```
  $ /home/loke/.cache/pre-commit/repoafysa_uk/py_env-python3.14/bin/mypy tests/conftest.py
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
