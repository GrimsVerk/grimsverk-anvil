# grimsverk-anvil — twin-run template test plan

This repository is a test bed. Its only purpose is to test
[grimsverk-template](https://github.com/GrimsVerk/grimsverk-template) on a real
run. The product it builds (a tiny unit-conversion CLI) is throwaway; the
findings about the template are the deliverable.

**The shape of the test.** One repository, one frozen starting point, two
identical unattended runs in parallel:

- `main` — the generated scaffold plus the canned design documents. Frozen
  once setup is done; no run merges into it.
- `run/local` — branched from `main`. Driven by `deliver-loop.sh` on the
  owner's machine, operated by a local Claude Code agent.
- `run/web` — branched from `main`. Driven by `/deliver-loop` in a Claude Code
  web session.

Both lanes build the same canned design (`docs/DESIGN.md`), which contains two
deliberate gaps (output precision; CLI syntax) and two pre-seeded backlog items
(BL-1, BL-2). That is the oracle bait: each run's planner must file
uncertainties, the oracle must rule, and stewards must plan from the rulings —
so every role runs: oracle, steward, planner, orchestrator, coder, blind
test-writer, reviewer, acceptance, and the driver itself.

The per-base-branch pipeline isolation this layout depends on landed in the
template as the fix for ESC-46 (`deliver-loop.sh --base`, lane branch
suffixes, `setup-github.sh --gate-branch`). **Do not start before that fix is
merged and released** (step 0).

---

## Part 1 — Owner setup (do this once, on your machine)

Everything here is copy-paste. Stop at any step that fails and fix it before
going on.

### 0. Confirm the template release carries the lane fix

```sh
gh release view -R GrimsVerk/grimsverk-template
```

The release notes must include "Scope the one-PR rule per base branch". Copier
generates from the **latest tag**, so if the fix is merged but a newer tag has
not appeared, wait for the release workflow, or stop and ask why it did not
run.

### 1. Generate the project

```sh
cd ~/code/GrimsVerk
copier copy https://github.com/GrimsVerk/grimsverk-template.git grimsverk-anvil
cd grimsverk-anvil
```

Answers:

| Question | Answer |
| --- | --- |
| `project_name` | press Enter (`grimsverk-anvil`) |
| `language` | `python` |
| `description` | `A tiny unit-conversion CLI that stress-tests the grimsverk-template pipeline` |
| `auto_merge` | press Enter (`true`) |
| `code_owner` | press Enter (`@GrimsVerk`) |

### 2. Make it a git repo and pull in the test kit

The canned documents land **before** the gates exist, in the same window the
scaffold commit uses. This round deliberately does not test `/design` or the
owner-landing of the design documents — see "Out of scope" at the bottom.

```sh
git init -b main
git add -A
git commit -m "Initial scaffold from grimsverk-template"
git log -1 --format='%an <%ae>'   # must show the GrimsVerk identity
git remote add origin git@github.com-grimsverk:GrimsVerk/grimsverk-anvil.git
git fetch origin claude/grimsverk-anvil-test-prep-86r4xu
git checkout FETCH_HEAD -- test-kit
cp test-kit/canned/DESIGN.md  docs/DESIGN.md
cp test-kit/canned/VISION.md  docs/VISION.md
cp test-kit/canned/BACKLOG.md docs/BACKLOG.md
git add -A
git commit -m "Add the anvil test kit and the canned test design"
```

### 3. Bootstrap the toolchain

```sh
uv sync
pre-commit install
```

### 4. Push, and make main the default branch

The prep branch was pushed to this repository first, so GitHub made **it** the
default branch. The pipeline needs `main` to be the default. Do not skip the
second command.

```sh
git push -u origin main
gh repo edit GrimsVerk/grimsverk-anvil --default-branch main
git remote set-head origin main   # the local clone must also know the default
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

## Part 3 — What the owner compares afterwards

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

## Out of scope this round

- The `/design` interview and the owner-authored landing gate for
  `docs/DESIGN.md` / `docs/VISION.md` (the canned docs land before the gates
  exist, deliberately, so the two lanes start byte-identical).
- `swift-ios`, the codex engine, `copier update` / `template-sync` on a real
  update, and glossary maintenance flows.
