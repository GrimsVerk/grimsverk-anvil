# grimsverk-anvil — twin-run template test plan

This repository is a test bed. Its only purpose is to test
[grimsverk-template](https://github.com/GrimsVerk/grimsverk-template) on a real
run. The product it builds (a tiny unit-conversion CLI) is throwaway; the
findings about the template are the deliverable.

**The shape of the test.** One repository, one frozen starting point, two
identical unattended runs in parallel:

- `main` — the test kit, the generated scaffold, and the canned design
  documents. Frozen once setup is done; no run merges into it.
- `run/local` — branched from `main`. Driven by `deliver-loop.sh` on the
  owner's machine, operated by a local Claude Code agent.
- `run/web` — branched from `main`. Driven by `/deliver-loop` in a Claude Code
  web session.

**This is a stress test, not a demo.** The canned inputs were built from the
template's own failure record — every escape in the template's
`docs/escapes.md`, the find_best_mobo postmortem
(`docs/projects/find_best_mobo/`), and the unverified-live list in
`docs/synthesis.md`. The design deliberately leaves questions open, the seeded
backlog contains items the pipeline must rule on, reject, and halt on, and the
milestone names are chosen so that careless plan slugs collide. The runs are
expected to hit friction; friction observed and recorded is the test working.

Both lanes build the same canned design (`docs/DESIGN.md`). The baits (all of
them mapped to expected machinery in Part 3):

- Three design gaps — output precision, CLI syntax, batch line format — so each
  lane's planner must file HIGH uncertainties instead of self-ruling (the
  find_best_mobo failure TB-3/ESC-41).
- A seeded escape (ESC-1, a floating-point artifact) and four seeded backlog
  items: BL-1 (aliases — should become an oracle requirement and a steward
  plan), BL-2 (absolute zero — same), BL-3 (demands the `rich` dependency,
  which vision tenet V5 forbids — the oracle's HALT path, never yet exercised),
  BL-4 (currency with live rates — contradicts the design's non-goals; should
  be dismissed, exercising the dismissal memory).
- Milestones named `convert` and `convert-batch` — one slug is a substring of
  the other, the exact collision class `plan-resolve.sh` hard-errors on.
- Strict numeric criteria (S1, S2, S5) meeting the undecided precision rule —
  a likely honest acceptance failure, which must route through a BL filing to
  the oracle, never be quietly passed.

So every role runs, in both lanes: oracle, steward, planner, orchestrator,
coder, blind test-writer, reviewer, acceptance, and the driver itself.

The per-base-branch pipeline isolation this layout depends on landed in the
template as the fix for ESC-46 (`deliver-loop.sh --base`, lane branch
suffixes, `setup-github.sh --gate-branch`), released as **v0.4.28**. Step 0
double-checks your generation will use it.

---

## Part 1 — Owner setup (do this once, on your machine)

Everything here is copy-paste. Stop at any step that fails and fix it before
going on. **Setup friction is test data too:** if any step fails, surprises
you, or needs a retry, jot one line (step number, what happened) into
`test-kit/reports/owner-setup.md`, commit it on `main` before step 6 or on a
`chore/test-report-setup` branch after, and push. The agents cannot see what
happened before they existed; this file is the only record of it.
(`scripts/setup-github.sh` records its own transcript automatically under
`docs/runs/setup/` — commit that too when it tells you to; your notes file
covers the steps the script does not see: copier, the clone, the web
environment.)

### 0. Confirm the template release and the default branch

```sh
gh release view -R GrimsVerk/grimsverk-template --json tagName --jq .tagName
gh repo view GrimsVerk/grimsverk-anvil --json defaultBranchRef --jq .defaultBranchRef.name
```

The first must print `v0.4.29` or newer — v0.4.28 carries the per-base lane
fix, v0.4.29 adds the evidence-recovery tools this plan's instructions use
(`deliver-loop.sh --land-evidence`, the setup transcript) — and copier
generates from the **latest tag**. The second
must print `main`; if it does not, fix it before anything else:

```sh
gh repo edit GrimsVerk/grimsverk-anvil --default-branch main
```

### 1. Clone the repo and render the scaffold into it

The test kit already lives on `main`, so the scaffold is rendered **into the
clone**, beside it. No file overlaps: the kit is entirely under `test-kit/`.

```sh
cd ~/code/GrimsVerk
git clone git@github.com-grimsverk:GrimsVerk/grimsverk-anvil.git
cd grimsverk-anvil
copier copy https://github.com/GrimsVerk/grimsverk-template.git .
```

Answers:

| Question | Answer |
| --- | --- |
| `project_name` | press Enter — but check the prompt offers `grimsverk-anvil`; if it offers anything else (or blank), type `grimsverk-anvil` |
| `language` | `python` |
| `description` | `A tiny unit-conversion CLI that stress-tests the grimsverk-template pipeline` |
| `auto_merge` | press Enter (`true`) |
| `code_owner` | press Enter (`@GrimsVerk`) |

If copier asks about overwriting any existing file, stop and look — it should
not, and an overwrite prompt means something unexpected is on `main`.

### 2. Commit the scaffold and install the canned design

The canned documents land **before** the gates exist, in the same window the
scaffold commit uses — direct commits to `main` are allowed here for exactly
that reason. This round deliberately does not test `/design` or the
owner-landing of the design documents — see "Out of scope" at the bottom.

```sh
git add -A
git commit -m "Initial scaffold from grimsverk-template"
git log -1 --format='%an <%ae>'   # must show the GrimsVerk identity
cp test-kit/canned/DESIGN.md  docs/DESIGN.md
cp test-kit/canned/VISION.md  docs/VISION.md
cp test-kit/canned/BACKLOG.md docs/BACKLOG.md
cp test-kit/canned/escapes.md docs/escapes.md
git add -A
git commit -m "Install the canned test design"
```

### 3. Bootstrap the toolchain

```sh
uv sync
pre-commit install
```

### 4. Push

```sh
git push origin main
```

### 5. Configure GitHub — gates on main AND on both lanes

```sh
scripts/setup-github.sh --app --verify \
  --gate-branch run/local --gate-branch run/web
```

It will prompt for `CLAUDE_CODE_OAUTH_TOKEN` (run `claude setup-token`),
`TEMPLATE_TOKEN` (your fine-grained template-read PAT), and the GitHub App id
plus `.pem` path (the App already exists from find_best_mobo — but you must
also **install** it on this repository: App settings → Install App →
grimsverk-anvil).

### 6. Create the two lanes

```sh
git branch run/local main
git branch run/web  main
git push origin run/local run/web
```

### 7. Read the configuration back before trusting it

```sh
RUN_BASE=run/local .github/scripts/unattended-ready.sh
RUN_BASE=run/web  .github/scripts/unattended-ready.sh
.claude/scripts/app-token.sh >/dev/null && echo "App identity OK"
```

All three must come back clean. A refusal names its own fix.

### 8. Prepare the web environment (for the web lane)

In claude.ai/code, create or edit the environment for
`GrimsVerk/grimsverk-anvil`:

**Environment variables**

| Name | Value |
| --- | --- |
| `GH_TOKEN` | a fine-grained PAT, repository `grimsverk-anvil` only: Contents RW, Pull requests RW, Checks RO |
| `GRIMSVERK_APP_ID` | the App id |
| `GRIMSVERK_APP_PEM_B64` | `base64 -w0 < your-app.private-key.pem` |
| `GRIMSVERK_APP_PRIVATE_KEY` | `/root/.config/grimsverk/app.pem` |

**Setup script**

```sh
set -e
mkdir -p /root/.config/grimsverk
printf '%s' "$GRIMSVERK_APP_PEM_B64" | base64 -d > /root/.config/grimsverk/app.pem
chmod 600 /root/.config/grimsverk/app.pem
if ! command -v gh >/dev/null 2>&1; then
  mkdir -p -m 755 /etc/apt/keyrings
  wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    > /etc/apt/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list
  apt-get update && apt-get install -y gh
fi
gh auth status
```

Network policy must allow `github.com` and `cli.github.com`. **If the web
session cannot get a working `gh`, the web driver refuses at preflight. That
refusal is a finding, not something to hack around — record it and stop the
web lane.**

### 9. Start the two runs

- Open a Claude Code session on your machine, in
  `~/code/GrimsVerk/grimsverk-anvil`, and paste `test-kit/PROMPT-LOCAL.md`
  (everything below its marker line), word for word.
- Open a Claude Code **web** session on `GrimsVerk/grimsverk-anvil` and paste
  `test-kit/PROMPT-WEB.md` (everything below its marker line), word for word.

Then walk away. Both runs stop on their own limits.

---

## Part 2 — Rules for the testing agents (both lanes)

You are testing the **template**, not building a product. The unit converter
is disposable; your findings are the deliverable. These rules bind both lanes.

1. **State your lane first.** Your run's base branch is in your prompt. Say it
   out loud before anything else, and never touch the other lane: its base
   branch, its `--<lane>`-suffixed branches, or its pull requests. If the
   machinery ever shows you the other lane's pull request as yours to wait on
   or fix, STOP and record it — that is a top-severity finding.
2. **Follow the project's AGENTS.md** exactly as a real run would. Do not
   invent shortcuts around the process; hitting friction IS the test working.
3. **Never modify the machinery.** `.github/`, `.claude/`, `AGENTS.md`,
   `CODEOWNERS`, pre-commit config are off-limits (they are anyway, per
   AGENTS.md). If a template bug blocks you: record it as a finding with the
   exact command and error, then either continue in project space only, or
   stop the lane if it cannot continue. Never "fix the template" from inside
   this repository.
4. **Keep a findings ledger as you go**, in `test-kit/reports/<lane>.md`
   (`local.md` or `web.md`), committed on branch `chore/test-report-<lane>`
   (`chore/test-report-local` or `chore/test-report-web`). Push the branch;
   do NOT open a pull request for it. Commit after every finding, not at the
   end — a crashed session must not take the ledger with it. Format:

   ```markdown
   ### F<n> — <one line>
   - Where: <setup step | phase | file | check name>
   - What happened: <exact command and exact output>
   - Expected: <what the template's docs say should happen>
   - Severity: blocker | bug | friction | docs
   ```

   Friction counts: a misleading message, a doc that says the wrong path, a
   step that needed a retry. If you are unsure whether something is a
   finding, it is a finding.
5. **Record phase transitions.** Every time the detector reports a PHASE,
   append one line to the ledger: timestamp, PHASE, and its key fields. This
   is the comparison spine between the two lanes.
6. **When your run stops** (any exit: done, limit, pattern, refusal), finish
   the ledger with a summary block: phases reached, pull requests opened and
   merged, oracle decisions written (OD ids), uncertainties filed (BL ids),
   criteria status, and the driver's own exit reason. Push it, then report to
   the owner in plain, high-level language (GLOSSARY.md rules apply).
7. **Do not restart a stopped run** and do not raise your own limits. One run
   per lane, then report.
8. **Rate-limit metering is itself under test (local lane).** The weekly-budget
   ceiling (`--budget-points`, read through `budget-probe.sh`) is the limit the
   owner will actually rely on, and it shipped broken once without anyone
   noticing (template ESC-32). So on the local lane: the driver's start banner
   must show a real gauge reading ("budget: weekly at N% …"); if it says no
   gauge is reachable, that is a **blocker finding** — do not fall back to
   PR/hour limits silently. During the run, confirm the budget line updates
   and, if the run stops on the allowance, record the exact stop message. The
   web lane has no gauge by design; note that the driver says so and asks for
   countable limits instead — anything else there is a finding.
9. **The observation checklist.** These are the template's "built but never
   observed live" claims (its synthesis file lists them). Recording each one,
   positively, is a core deliverable of your run — "did not check" is not an
   allowed value:
   - After every merged pull request: did its head branch disappear, when, and
     by which path (immediately, or the nightly sweep)? No branch has ever
     been observed to vanish; four wrong theories are on record (ESC-21).
   - Does `arm-auto-merge` appear in every PR's check list, and does the merge
     actually complete without a human (ESC-36)?
   - Is every pipeline pull request authored by the GitHub App (`…[bot]`), and
     never by the owner (ESC-26, ESC-35)?
   - For every required check on every PR: its DURATION. A check that should
     take a minute finishing in ~1 second is a skip reporting success
     (ESC-45) — record it as a finding even though it is green.
   - After the run stops: does `docs/runs/<timestamp>/` contain the run
     report, `reviews/` payloads with no `MISSING.md` (ESC-43), and `workers/`
     logs (ESC-42)? Did the run-evidence pull request itself merge (ESC-40)?
   - When the OTHER lane merges a pull request while yours is open: was your
     PR auto-updated by the App with its checks re-running (the
     `update-open-prs` job, ESC-17 — never observed live)?
10. **Contamination is a probe.** Pipeline workers derive from the design
    layer; nothing in `test-kit/` is theirs to read. If any pipeline artifact
    (a plan, a ruling, a commit message) quotes or references `test-kit/`,
    record it as a finding — it means a worker roamed outside its inputs.
11. **A triggered failsafe is itself a finding, always, and says so by name.**
    The template promises to land its own evidence at every stop — run
    report, reviews, worker logs, the evidence pull request. The failsafes in
    this kit (the ledger paste, the raw-log copy, `--land-evidence`, any
    manual securing) exist for when that promise breaks. So whenever a
    failsafe — not the template's own machinery — is what preserved a piece
    of evidence, file a finding titled exactly
    `TEMPLATE SELF-RECORDING FAILURE: <what the template failed to record,
    and which failsafe caught it>`, severity bug or higher. Never fold this
    into a general summary line: the failsafe working is the anvil doing its
    job; the failsafe being NEEDED is the template failing at the exact
    failure mode this whole test exists to catch, and it must be reported
    upstream as its own row.

## Part 3 — What the owner compares afterwards

### The bait map — what each planted input should have produced

Check each row in BOTH lanes. A bait that produced nothing, or produced
something different from the expected mechanism, is a finding about the
template (or, sometimes, about the bait — say which).

| Bait | Expected mechanism | Where to look |
| --- | --- | --- |
| Precision gap (§11) + seeded ESC-1 | planner files a HIGH `BL-<n>` and stops; oracle rules, citing ESC-1; ruling names how it will be measured | `docs/BACKLOG.md` uncertainties, `docs/DESIGN.oracle.md`, the plans |
| CLI-syntax gap (§11) | second HIGH uncertainty, same route — external interface, so never self-ruled | same |
| Batch line format gap (§11) | uncertainty filed no later than the `convert-batch` milestone plan | same |
| BL-1 aliases | oracle decision adds an R1000+ requirement; a steward plans it; it gets built | `docs/DESIGN.oracle.md`, `docs/plans/oracle/`, merged `feat/` PRs |
| BL-2 absolute zero | same route as BL-1 | same |
| BL-3 `rich` dependency | vision tenet V5 forbids it: expect a HALT entry (the never-exercised path), or an explicit rejection quoting V5 verbatim — record which | `docs/DESIGN.oracle.md` |
| BL-4 currency | contradicts the design's non-goals: dismissed in the handoff's do-not-act list, and NOT re-handed to the oracle every iteration | `docs/oracle/handoff-*.md`, the run report's phase lines |
| `convert` / `convert-batch` slugs | if a plan slug lands as a substring of another, `plan-resolve.sh` hard-errors and a fix session must rename — record whether the planner avoided the trap or the gate caught it | the `plan` check output, plan front matter |
| Strict S1/S2/S5 vs undecided precision | if an acceptance script fails honestly: recorded as fail AND filed as a `BL-<n>`, routed to the oracle — never quietly passed, possibly waived with a reason | `docs/acceptance.md`, `acceptance/`, `docs/BACKLOG.md` |
| S4 (owner) criterion | the run ends pending-on-owner for S4 and says exactly what you should run — never reports itself fully done | the final report, `docs/acceptance.md` |

### The comparison

- The two ledgers: `test-kit/reports/local.md` vs `web.md` — same phases, same
  order, similar counts?
- `docs/runs/<timestamp>/` evidence on each lane (run report, review payloads).
- Each lane's `docs/DESIGN.oracle.md`: did both oracles rule on BL-1, BL-2 and
  the planner-filed uncertainties? Are the rulings comparable?
- Each lane's acceptance table (`docs/acceptance.md`) and criteria scripts.
- `git diff run/local run/web -- src tests` for divergence between the two
  builds (interesting, not a failure).
- Every finding of severity blocker/bug becomes a candidate `docs/escapes.md`
  entry in the **template** repository, with the ratchet applied there.

### Your own closing actions (each is itself a live test)

1. **Approve and merge each lane's acceptance pull request.** It must be
   authored by the App — which is the only reason you CAN approve it (GitHub
   refuses an author's own approval; ESC-35 predicted this works and nothing
   has ever observed it).
2. **Run S4** (the owner criterion) on your machine, offline, per lane, and
   record the verdict in each lane's `docs/acceptance.md`.
3. Check the ruleset held: no pipeline PR merged red, and nothing pushed
   straight to `main`, `run/local`, or `run/web`.

## Coverage, honestly

**Explicitly IN scope** — the template's five "unverified-live" items
(synthesis §1.1) all get their first live observation here: a branch vanishing
after auto-merge, REST-created rulesets gating before checks first report, the
budget probe against a real subscription, the driver's real session command
lines, and `/deliver-loop` web mode watched end to end.

**Out of scope this round** — say so in any report rather than implying it was
covered:

- The `/design` interview and the owner-authored landing gate for
  `docs/DESIGN.md` / `docs/VISION.md` (the canned docs land before the gates
  exist, deliberately, so the two lanes start byte-identical).
- `copier update` / `template-sync` on a real update — including the conflict
  path (template ESC-14). **Checked and recorded 2026-08-19, not skipped by
  oversight:** the owner asked whether the evidence-hardening template release
  could be pulled in via `copier update` as a live mid-run-update test. It
  cannot yet — this repository holds only the test kit until setup Part 1
  renders the scaffold, and `copier update` needs the `.copier-answers.yml`
  that only generation creates. There was no update to attempt, so there is no
  failure to log. The runs will simply generate FROM the release that already
  carries the hardening. The live update test arms itself naturally: the
  first template release that appears AFTER generation is the payload — run
  `scripts/update-from-template.sh` on `main` then, and that is the ESC-14 /
  `template-sync` live test. Candidate for whichever lane survives better.
- `swift-ios`, the codex engine, and glossary maintenance flows.
- Attended orchestration (`/orchestrate` driven by a human session): both lanes
  run the unattended path only.
