# WEB lane findings ledger

- Lane: **web**
- Base branch for the run: `run/web`
- Ledger branch: `chore/test-report-web` (branched off `main`, pushed, never a pull request)
- Session started: 2026-08-19T21:33:20Z
- Operator identity intended: the GitHub App (ID 4635498), minted per turn

---

## Setup log — TESTPLAN Part 1

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 2026-08-19T21:33:20Z | 1W — get the repository | OK. Session started with `GrimsVerk/grimsverk-anvil` checked out on `claude/web-lane-pipeline-test-a029r2`, remote `https://github.com/GrimsVerk/grimsverk-anvil`. Working tree clean, only `test-kit/` present. No other repository attached, read, or cloned at any point (Part 2 rule 12 held). |
| 2026-08-19T21:33:20Z | pre-flight — environment inventory | **FAILED.** `/tmp/anvil-env-setup.log` does not exist; `/root/.config/grimsverk/` does not exist; `GRIMSVERK_APP_ID`, `GRIMSVERK_APP_PEM_B64` and `GRIMSVERK_APP_PRIVATE_KEY` are all unset; `gh` and `copier` are both absent from `PATH`. |
| 2026-08-19T21:33:37Z | credential mint (`test-kit/bootstrap/app-token.sh`) | **FAILED, exit 3** — "the App identity is not set up yet." See F1. |
| — | 2 — confirm template release ≥ v0.4.31 | **NOT REACHED.** Needs `gh` plus an App token; neither exists. |
| — | 3W — branch `run/web` off `main`, render scaffold with copier | **NOT REACHED.** Needs the App token for the git URL rewrite, and `copier` is not installed. |
| — | 4 — install canned inputs | **NOT REACHED.** |
| — | 5 — `uv sync`, `pre-commit install`, commit | **NOT REACHED.** |
| — | 6 — push `run/web` (bounded retry, 3 min x 45) | **NOT REACHED.** Nothing to push; the branch `run/web` was never created. |
| — | 7W — bounded wait for gating (`unattended-ready.sh --runtime`) | **NOT REACHED.** The script ships inside the scaffold, which was never rendered. |
| — | /deliver-loop run on base `run/web` | **NOT STARTED.** |

The lane is stopped at the credential mint, per the operator prompt: "If the
mint fails, the environment is missing its App id or key: record the exact
error (and quote `/tmp/anvil-env-setup.log` if it exists) as a blocker
finding, push the ledger, and stop the lane."

---

## Findings

### F1 — BLOCKER: the web environment has no App credential; the Part 0 setup script never ran
- Where: TESTPLAN Part 1 step 3W, credential mint via `test-kit/bootstrap/app-token.sh`. Root cause sits upstream in TESTPLAN Part 0 (the claude.ai web environment for grimsverk-anvil).
- What happened:

  Exact command and exact output:

  ```
  $ test-kit/bootstrap/app-token.sh
  app-token: the App identity is not set up yet.

  No .claude/app-identity and no skeleton beside it.

  WHY THIS BLOCKS THE RUN. The unattended driver opens pull requests, and it must
  open them as someone who is NOT you. Otherwise .github/scripts/owner-authored.sh
  compares your login to your login, passes, and docs/DESIGN.md and docs/VISION.md
  have no protection for the whole run — the check prints its guarantee without
  holding it. So this refuses rather than warning.
  [... the script's full end-to-end App setup instructions follow ...]
  $ echo $?
  3
  ```

  Exit code 3 is the script's documented "not configured at all" path.

  Supporting evidence, all gathered before the mint:

  ```
  $ cat /tmp/anvil-env-setup.log
  cat: /tmp/anvil-env-setup.log: No such file or directory

  $ ls -la /root/.config/grimsverk/
  ls: cannot access '/root/.config/grimsverk/': No such file or directory

  $ env | grep -c GRIMSVERK
  0

  $ command -v gh   || echo "gh NOT INSTALLED"
  gh NOT INSTALLED
  $ command -v copier || echo "copier NOT INSTALLED"
  copier NOT INSTALLED
  ```

  The absence of `/tmp/anvil-env-setup.log` is the decisive item. That log is
  written by the FIRST line of the Part 0 setup script (`date -u ... >>
  /tmp/anvil-env-setup.log`), before anything that could fail. No log means the
  script did not run at all — this is not a partial failure, a bad key, or a
  revoked App. The three symptoms that follow (no `.pem` at
  `/root/.config/grimsverk/app.pem`, no `gh`, no `copier`) are each a separate
  action of that same script, and all three are missing, which is consistent.

  Note on which failure this is: the environment variables `GRIMSVERK_APP_ID`,
  `GRIMSVERK_APP_PEM_B64` and `GRIMSVERK_APP_PRIVATE_KEY` are ALSO unset. Those
  are environment variables, not script output — they are configured on the
  claude.ai environment itself and would be present even if the setup script had
  run and failed. Their absence says the environment definition is missing its
  variables, and the setup script, having no `GRIMSVERK_APP_PEM_B64` to decode,
  could not have produced a usable `.pem` even if it had run. So there are two
  defects stacked: the environment variables are not on the environment, and the
  setup script did not execute.
- Expected: TESTPLAN Part 0 states the claude.ai web environment for
  grimsverk-anvil "must carry the environment variables `GRIMSVERK_APP_ID`
  (4635498), `GRIMSVERK_APP_PEM_B64`, `GRIMSVERK_APP_PRIVATE_KEY`
  (`/root/.config/grimsverk/app.pem`) and this setup script". The plan further
  says the log exists "so the web agent can quote a real error instead of
  guessing whether setup ran (a round-1 finding)". Neither the variables nor
  the log are present, so step 3W's token mint cannot succeed and the entire
  web lane cannot start.
- Severity: **blocker**
- Lane impact: the web lane never started. No `run/web` branch was created, no
  scaffold rendered, no pull request opened, no phase reached.
- Remedy for the owner (rig-side, not template-side): on the claude.ai
  environment for grimsverk-anvil, set `GRIMSVERK_APP_ID=4635498`,
  `GRIMSVERK_APP_PEM_B64=$(base64 -w0 < the .pem)` and
  `GRIMSVERK_APP_PRIVATE_KEY=/root/.config/grimsverk/app.pem`, and confirm the
  Part 0 setup script is attached to the environment and runs at session start.
  Confirm by checking that `/tmp/anvil-env-setup.log` exists in a fresh session.

### F2 — the round-1 log fix worked exactly as designed, and it is the reason F1 is diagnosable
- Where: TESTPLAN Part 0, `/tmp/anvil-env-setup.log`.
- What happened: the log's ABSENCE, not its contents, is what distinguished
  "the setup script ran and something inside it failed" from "the setup script
  never ran". Round 1's finding was that the web agent had to guess. This round
  no guessing was needed, and the guess would have been wrong: without the log
  the natural reading of the `app-token.sh` error is "bad or missing key",
  which points the owner at the App, at the `.pem`, and at the installation —
  three places that are all fine. The real defect is one level up, on the
  environment definition.
- Expected: this is the fix behaving as intended.
- Severity: **docs** (recorded as a positive observation, per Part 2 rule 4's
  "if you are unsure whether something is a finding, it is a finding")

### F3 — an ambient non-App GitHub credential is present in the web session
- Where: the web session environment, observed during the pre-flight inventory.
- What happened: `GH_TOKEN` and `GITHUB_TOKEN` are both set in the session
  environment by the Claude Code web harness, independent of the test rig. They
  were NOT used — the operator prompt names the App as the only permitted
  GitHub credential, and no `gh` command was run at any point in this session
  (`gh` is not installed either way). They are recorded because their presence
  is a live trap for exactly the guarantee this test exists to check: TESTPLAN
  step 3W tells the web agent to `export GH_TOKEN="$TOKEN"` from the App mint.
  In a session where the harness has already exported `GH_TOKEN`, an agent that
  skipped or fumbled the mint would still find a working `GH_TOKEN` in its
  environment and would open pull requests under the harness identity instead
  of `app[bot]` — silently defeating ESC-26 / ESC-35, with green checks
  throughout. Nothing in the template or the plan warns about this collision.
- Expected: TESTPLAN Part 1 step 3W reuses the name `GH_TOKEN` with no
  precondition check that it was unset beforehand, and no post-mint assertion
  that the exported value is the App's.
- Severity: **friction** — it did not bite this round only because the mint
  failed loudly first and `gh` was absent. Suggested hardening for the
  template: after minting, assert the identity (`gh api user --jq .login` must
  end in `[bot]`) before the first `gh pr create`, so a stale ambient token
  cannot pass itself off as the App.

---

## Observation checklist (Part 2 rule 9)

Every item is unobservable this round because no pipeline pull request was ever
opened. Recorded explicitly rather than left blank, since "did not check" is
not an allowed value:

| Item | Status |
| --- | --- |
| Merged PR head branch disappears — when, and by which path (ESC-21) | Not observable — no PR was opened. |
| `arm-auto-merge` present in every PR's check list; merge completes without a human (ESC-36) | Not observable — no PR was opened. |
| Every pipeline PR authored by the App (`…[bot]`), never the owner (ESC-26, ESC-35) | Not observable — no PR was opened. See F3 for a related risk found without a PR. |
| Duration of every required check; ~1s green = a skip reporting success (ESC-45) | Not observable — no checks ever ran. |
| `docs/runs/<timestamp>/` holds run report, `reviews/` with no `MISSING.md` (ESC-43), `workers/` logs (ESC-42); evidence PR merged (ESC-40) | Not observable — no run started, no scaffold rendered. |
| Other lane's merge auto-updates this lane's open PR, checks re-run (`update-open-prs`, ESC-17) | Not observable — this lane had no open PR. |
| Contamination probe: any pipeline artifact quoting `test-kit/` (rule 10) | Not observable — no pipeline artifact was produced. |
| Web lane says no usage gauge is reachable and asks for countable limits (rule 8) | Not observable — `/deliver-loop` never started. |

---

## Summary (Part 2 rule 6)

- **Phases reached:** none. The run never started; the lane stopped during
  TESTPLAN Part 1 setup, at the step-3W credential mint.
- **Pull requests opened:** 0. **Merged:** 0.
- **Oracle decisions written (OD ids):** none.
- **Uncertainties filed (BL ids):** none.
- **Criteria status:** not evaluated; `docs/acceptance.md` was never rendered.
- **Driver's own exit reason:** the driver was never started. The lane was
  stopped by the operator, per the standing instruction to stop on a failed
  credential mint.
- **Findings:** 3 — one blocker (F1), one positive observation (F2), one
  friction (F3).
- **Bait map (Part 3):** every row is untested this round. No bait was reached.
- **Template verdict:** this round tested the RIG, not the template. F1 is an
  environment-configuration defect on the owner's side, not a template bug —
  the template's own refusal behaved correctly and loudly, exactly as its
  comments promise, and F2 shows the round-1 diagnostic fix earning its keep.
  The web lane produced no evidence about the template's pipeline.
- **No failsafe was triggered** in the Part 2 rule 11 sense: no template
  self-recording promise was broken, because no run ever reached the point of
  making one. This ledger is the primary record, not a rescue of one.
- **`main` was never touched.** No commit, no push, no reset. The `run/web`
  branch was never created. The `run/local` lane, its branches, and its pull
  requests were never read or touched.
