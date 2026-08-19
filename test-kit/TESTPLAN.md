# grimsverk-anvil — twin-run template test plan

This repository is a test bed. Its only purpose is to test
[grimsverk-template](https://github.com/GrimsVerk/grimsverk-template) on a real
run. The product it builds (a tiny unit-conversion CLI) is throwaway; the
findings about the template are the deliverable.

**The shape of the test.** One repository, one frozen starting point, two
identical unattended runs in parallel — and NOBODY ever pushes to `main`:

- `main` — the test kit, and nothing else, forever. Both agents branch off it
  and never touch it or each other's branches again.
- `run/local` — branched from `main` by the local agent, which renders its OWN
  scaffold there, does its own setup, and drives `deliver-loop.sh` on the
  owner's machine.
- `run/web` — branched from `main` by the web agent, which renders its OWN
  scaffold there and drives `/deliver-loop` in a Claude Code web session.

The two scaffolds come from the same template release with the same answers,
so they are expected to be near-identical — and diffing them afterwards is
itself part of the comparison.

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
suffixes, `setup-github.sh --gate-branch`); everything the lanes need is in
release **v0.4.31**, and Part 1 step 2 refuses anything older.

---

## Part 0 — One-time rig (owner, already done, survives every wipe)

Nothing here repeats per round. It is listed so a refusal can be traced, not
so anyone redoes it: the GitHub App (ID 4635498) with Contents RW, Pull
requests RW, Checks RO — installed on **grimsverk-anvil and
grimsverk-template**; the repository secrets `CLAUDE_CODE_OAUTH_TOKEN`,
`APP_ID`, `APP_PRIVATE_KEY` (secrets survive branch wipes); and the claude.ai
web **environment** for grimsverk-anvil, which must carry the environment
variables `GRIMSVERK_APP_ID` (4635498), `GRIMSVERK_APP_PEM_B64` (`base64 -w0 <
the .pem`), `GRIMSVERK_APP_PRIVATE_KEY` (`/root/.config/grimsverk/app.pem`)
and this setup script (network policy must allow `github.com` and
`cli.github.com`):

```sh
set -e
date -u +"env-setup ran %Y-%m-%dT%H:%M:%SZ" >> /tmp/anvil-env-setup.log
mkdir -p /root/.config/grimsverk
printf '%s' "$GRIMSVERK_APP_PEM_B64" | base64 -d > /root/.config/grimsverk/app.pem
chmod 600 /root/.config/grimsverk/app.pem
command -v uv >/dev/null 2>&1 && uv tool install copier >> /tmp/anvil-env-setup.log 2>&1 || true
if ! command -v gh >/dev/null 2>&1; then
  mkdir -p -m 755 /etc/apt/keyrings
  wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    > /etc/apt/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list
  apt-get update >> /tmp/anvil-env-setup.log 2>&1 && apt-get install -y gh >> /tmp/anvil-env-setup.log 2>&1
fi
```

The script logs to `/tmp/anvil-env-setup.log` so the web agent can quote a
real error instead of guessing whether setup ran (a round-1 finding).

**Wiping between rounds (owner):** delete every branch except `main`. Secrets,
the ruleset, the App, and the web environment all stay; the stale ruleset
still names the old lane branches, and the local agent's first setup run
resets it (step 6a below).

---

## Part 1 — Lane setup: each agent does ALL of this itself, on its own branch

Principles, before the steps:

- **`main` is untouchable.** It carries the kit and nothing else. No commit,
  no push, no reset — ever, by anyone.
- **Each lane renders its own scaffold on its own branch** with copier, from
  the template's latest release. Same release, same answers — the two
  scaffolds should come out near-identical, and that is checked afterwards.
- **The one sanctioned asymmetry:** only the local agent holds admin power
  (the owner's `gh` login). The web agent's identity is the App, which is
  deliberately weaker — it cannot edit rulesets or secrets, and must never be
  able to. So ALL ruleset work belongs to the local agent, **including gating
  the web lane's branch**, and the web agent waits (bounded) for that. This
  is repository configuration, not a touch of the other lane's content.

The steps. `<lane>` is `run/local` or `run/web`; lines marked **L:** are the
local lane only, **W:** the web lane only.

### 1. Get the repository

- **L:** clone with the owner's SSH alias, into the standard location:
  `cd ~/code/GrimsVerk && git clone
  git@github.com-grimsverk:GrimsVerk/grimsverk-anvil.git && cd
  grimsverk-anvil` (the plain `git@github.com:` host has no key attached).
- **W:** the session starts with the repository checked out. Touch no other
  repository (Part 2, rule 12) — do not attach, add, or clone anything else.

### 2. Confirm the template release

The latest release of grimsverk-template must be **v0.4.31 or newer** (it
carries the per-base lanes, the evidence recovery tools, the App-only
credentials, and the two fixes from round 1). **L:** `gh release view -R
GrimsVerk/grimsverk-template --json tagName --jq .tagName`. **W:** query the
API with `gh` after step 3W's token mint, or read the tag copier resolves in
`.copier-answers.yml` after rendering and stop if it is older.

### 3. Create your lane branch, then render the scaffold ON IT

```sh
git switch -c <lane> origin/main
```

Render with copier — the scaffold lands on your branch, never on `main`:

- **L:** copier is a machine tool (`uv tool install copier` if missing); the
  owner's gitconfig routes the template's https URL over SSH. Run
  `copier copy https://github.com/GrimsVerk/grimsverk-template.git .`
- **W:** the template is private and this session must NOT attach or clone
  it. The one permitted read is copier's own fetch, authenticated by a token
  minted from the App:

  ```sh
  TOKEN="$(test-kit/bootstrap/app-token.sh)"
  git config --global url."https://x-access-token:${TOKEN}@github.com/".insteadOf "https://github.com/"
  copier copy https://github.com/GrimsVerk/grimsverk-template.git .
  export GH_TOKEN="$TOKEN"   # gh's credential, same mint; re-mint every turn
  ```

  `_src_path` must record the canonical `https://github.com/...` URL — never
  a token, never a local path.

Answers, both lanes, exactly:

| Question | Answer |
| --- | --- |
| `project_name` | `grimsverk-anvil` (press Enter if offered; type it if not) |
| `language` | `python` |
| `description` | `A tiny unit-conversion CLI that stress-tests the grimsverk-template pipeline` |
| `auto_merge` | `true` (Enter) |
| `code_owner` | `@GrimsVerk` (Enter) |

If copier asks to overwrite an existing file, stop and look — the kit is
entirely under `test-kit/`, so there is no legitimate overlap.

### 4. Install the canned test inputs

```sh
cp test-kit/canned/DESIGN.md  docs/DESIGN.md
cp test-kit/canned/VISION.md  docs/VISION.md
cp test-kit/canned/BACKLOG.md docs/BACKLOG.md
cp test-kit/canned/escapes.md docs/escapes.md
```

### 5. Toolchain BEFORE the first commit, then commit everything

The CI `checks` job runs `uv sync --locked`, so `uv.lock` must ride in the
scaffold commit (template ESC-47 — round 1 found this the hard way):

```sh
uv sync
pre-commit install
git add -A
git commit -m "Scaffold and canned test design (<lane>)"
```

**L:** check the identity: `git log -1 --format='%an <%ae>'` must show
GrimsVerk.

### 6. Push your lane — and what a rejection means

```sh
git push -u origin <lane>
```

If the push is rejected with "required status checks have not succeeded", a
ruleset from a previous round still names your lane. That is expected on the
first round after a wipe:

- **L:** do step 6a first — your own ruleset reset unblocks you — then push
  again.
- **W:** wait and retry every 3 minutes, up to 45 (the local agent's reset
  unblocks you); log each attempt with a timestamp in your ledger. Past 45
  minutes: blocker finding, stop the lane.

### 6a. LOCAL ONLY — the rig duties

1. From your branch (the scaffold is there now), run the setup **without**
   `--gate-branch` and **without** `--verify`:

   ```sh
   scripts/setup-github.sh --app
   ```

   This resets the `grimsverk-gates` ruleset to the default branch only
   (unblocking lane creation for BOTH lanes), asserts the merge settings, and
   leaves the existing secrets alone. If it prompts for the App ID and `.pem`
   path, the values are in your prompt. Do NOT pass `--verify`: `main`
   carries no workflows, so its throwaway pull request would wait forever;
   the checks register on the first real lane pull request instead.
2. Ensure the driver's local identity file exists —
   `cp .claude/app-identity.example .claude/app-identity`, fill in the App ID
   and `.pem` path from your prompt — then prove it:
   `.claude/scripts/app-token.sh >/dev/null && echo "App identity OK"`.
3. Push your lane (step 6) if not already done.
4. **Gate BOTH lanes once both exist.** Poll
   `git ls-remote --heads origin 'run/*'` every 3 minutes, up to 45, until
   `run/web` appears, then:

   ```sh
   scripts/setup-github.sh --app --gate-branch run/local --gate-branch run/web
   ```

   If `run/web` never appears within the bound: gate `run/local` alone,
   record a finding, continue — the web lane reports its own absence.

### 7. Verify readiness, then start your driver

- **L:** `RUN_BASE=run/local .github/scripts/unattended-ready.sh` (the full
  check — you are the admin identity). All green, then start the driver per
  your prompt.
- **W:** poll `RUN_BASE=run/web .github/scripts/unattended-ready.sh
  --runtime` every 3 minutes, up to 45, logging timestamps — it goes green
  when the local agent's step 6a-4 lands. Then start `/deliver-loop` per your
  prompt. Past 45 minutes still ungated: blocker finding, stop the lane.

---

## Part 2 — Rules for the testing agents (both lanes)

You are testing the **template**, not building a product. The unit converter
is disposable; your findings are the deliverable. These rules bind both lanes.

1. **State your lane first.** Your run's base branch is in your prompt. Say it
   out loud before anything else, and never touch the other lane: its base
   branch, its `--<lane>`-suffixed branches, or its pull requests. **And never
   touch `main`** — no commit, no push, no reset, under any instruction short
   of the owner themselves; `main` is the kit and the common ancestor, and a
   run that moves it contaminates both lanes. If the
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
12. **The web lane sees exactly one repository: grimsverk-anvil.** Never
    attach, add, clone, fetch, or read any other repository from the web
    session — including grimsverk-template. (Round 1's web agent attached the
    template to its session; the owner ruled that out.) The single sanctioned
    exception is copier's own template fetch in Part 1 step 3W, authenticated
    by the App token through the git URL rewrite — copier reads the template
    so it can render; the agent never does. `_src_path` must end up as the
    canonical https URL. The local lane reads the template only the same way,
    through copier.

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
- The two SCAFFOLDS: `git diff run/local run/web -- ':!src' ':!tests'
  ':!docs' ':!test-kit'` should be near-empty (same release, same answers);
  any difference is either copier nondeterminism or a lane deviating from
  Part 1 — find out which.
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
