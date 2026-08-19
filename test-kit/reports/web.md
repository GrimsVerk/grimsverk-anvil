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
| 2026-08-19T21:50:47Z | session 2 — owner attached the Part 0 setup script; platform reported "Setup script failed with exit code 8" | **FAILED.** Root cause identified: `cli.github.com` is not on the environment's network allowlist. See F4. Environment still carries no `GRIMSVERK_*` variables and no artifacts from the script — see F5. Lane remains stopped. |
| 2026-08-19T22:29:14Z | session 3 — Part 0 environment rebuilt by the owner | **OK.** F1/F4/F5 are resolved rig-side. `/tmp/anvil-env-setup.log` now exists; `gh` 2.97.0 installed from `cli.github.com` with no 403; `copier` and `uv` on PATH; `GRIMSVERK_APP_ID=4635498` and `GRIMSVERK_APP_PRIVATE_KEY=/root/.config/grimsverk/app.pem` both set. |
| 2026-08-19T22:31Z | session 3 — key delivery by owner paste | **OK.** Written verbatim to `/root/.config/grimsverk/app.pem`, mode `600`. `openssl rsa -noout -check` → `RSA key ok`; `Private-Key: (2048 bit, 2 primes)`. Never printed, committed, or pushed. |
| 2026-08-19T22:32:3xZ | session 3 — step 3W credential mint | **FAILED, exit 4** — GitHub answered `401` to the App's JWT. See F7. |
| 2026-08-19T22:33Z | session 3 — mint retried once | **FAILED identically.** Byte-identical output; not transient. |
| — | session 3 — steps 2, 3W render, 4, 5, 6, 7W, /deliver-loop | **NOT REACHED.** Each one needs the App token. Lane stopped again, one step further along than session 2. |

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


### F4 — BLOCKER: the Part 0 setup script dies at `cli.github.com`, which the environment's network policy denies
- Where: TESTPLAN Part 0, the claude.ai web environment setup script for grimsverk-anvil. Observed in session 2 (2026-08-19T21:50Z), reported by the platform as "Setup script failed with exit code 8. Edit your environment's setup script and start a new session."
- What happened: the script's `gh` install block fetches the apt keyring:

  ```sh
  wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    > /etc/apt/keyrings/githubcli-archive-keyring.gpg
  ```

  The session's egress proxy denies that host. Reproduced directly:

  ```
  $ wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg > /tmp/kr.gpg
  $ echo $?
  4
  $ ls -la /tmp/kr.gpg
  -rw-r--r-- 1 root root 0 Aug 19 21:51 /tmp/kr.gpg
  ```

  and named explicitly by the proxy's own status endpoint:

  ```
  $ curl -sS "$HTTPS_PROXY/__agentproxy/status"
  ...
  "recentRelayFailures": [
    {
      "ts": "2026-08-19T21:51:28.171Z",
      "kind": "connect_rejected",
      "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
      "host": "cli.github.com:443"
    }
  ]
  ```

  `wget` exit 8 is documented as "Server issued an error response" — the proxy's
  403. (Interactively the same fetch reports exit 4, a network failure; the
  difference is only how the proxy refuses at that moment. Both are the same
  denial, and both are fatal under the script's `set -e`.)

  Nothing else in the script is at fault. Everything the script needs besides
  that one host is reachable from the session, verified individually:

  | Host / action | Result |
  | --- | --- |
  | `api.github.com` (what `app-token.sh` calls) | HTTP 200 — fine |
  | `git` push/fetch over `https://github.com` | works — the ledger pushed over it |
  | `uv tool install copier` (pypi, direct-allowed) | succeeded; `copier` now on PATH |
  | `cli.github.com` (the keyring and apt repo) | **403 CONNECT — denied** |

  No alternative route to `gh` exists from inside the session. Fetching the
  release tarball from `github.com/cli/cli` is refused too, because the
  session's GitHub access is repository-scoped to grimsverk-anvil:

  ```
  $ curl -sS https://api.github.com/repos/cli/cli/releases/latest
  {"message":"GitHub access to this repository is not enabled for this session. ..."}
  ```

  That refusal is correct and was not worked around — Part 2 rule 12 forbids
  attaching any other repository, and `cli/cli` is another repository.
- Expected: TESTPLAN Part 0 states the environment's "network policy must allow
  `github.com` and `cli.github.com`". `github.com` is allowed; `cli.github.com`
  is not. The plan names the requirement correctly; the environment does not
  satisfy it.
- Severity: **blocker**
- Remedy: add `cli.github.com` to the environment's network allowlist. This is
  environment configuration, not a script change — but see F5 for why the
  script should be hardened regardless.

### F5 — BUG: a failing setup script appears to discard the entire environment build, credential included
- Where: TESTPLAN Part 0 script structure, interacting with the claude.ai web environment's build behaviour.
- What happened: the script begins with `set -e`, and the failing `wget` sits in
  the LAST block. So the four earlier actions — write
  `/tmp/anvil-env-setup.log`, `mkdir -p /root/.config/grimsverk`, decode the
  `.pem`, `uv tool install copier` — all run before the failure and all of them
  should have left artifacts behind. None survived into the session:

  ```
  $ cat /tmp/anvil-env-setup.log
  cat: /tmp/anvil-env-setup.log: No such file or directory
  $ ls -la /root/.config/grimsverk/
  ls: cannot access '/root/.config/grimsverk/': No such file or directory
  $ command -v copier || echo "copier MISSING"
  copier MISSING
  $ env | grep -o '^GRIMSVERK[A-Z_]*'
  (no output)
  ```

  The most consistent reading is that the platform treats a non-zero setup
  script as a failed environment build and runs the session from the base image
  instead, discarding every filesystem change the script made. The
  `GRIMSVERK_*` environment variables are absent as well, which suggests the
  discarded build takes the environment's variable set with it — though this
  round cannot separate that from "the variables were never added", since they
  were also absent in session 1 before the script was ever attached.

  Either way the consequence is the one that matters: **an optional convenience
  (`gh` via apt) took the mandatory credential down with it.** The App `.pem` is
  the one artifact the whole lane depends on, it is produced by line 4, and it
  was lost because line 20 could not reach a host.
- Expected: TESTPLAN Part 0 presents the script as a sequence of independent
  provisioning steps. Nothing in the plan warns that a late failure voids the
  early steps, and the script's own `set -e` guarantees it.
- Severity: **bug** (in the rig's script design, not in the template)
- Remedy: drop `set -e`, do the credential first, make every network-dependent
  step non-fatal, and end with an explicit `exit 0`. A corrected script is in
  the appendix below and is the recommended replacement.

### F6 — the App identity has no path into the session that does not depend on environment variables
- Where: TESTPLAN Part 0 / Part 1 step 3W, `test-kit/bootstrap/app-token.sh`.
- What happened: `app-token.sh` finds its credentials in exactly two places —
  the `GRIMSVERK_APP_ID` / `GRIMSVERK_APP_PRIVATE_KEY` environment variables, or
  an identity FILE at `.claude/app-identity`. In the web lane before rendering,
  the file cannot exist: `.claude/` only appears once the scaffold is rendered,
  and rendering is the very thing the token is needed for. So the environment
  variables are the single point of failure for the entire lane, and they have
  now been absent in two consecutive sessions.
- Expected: the plan assumes the variables reach the agent's shell. That
  assumption is untested and, on this evidence, unreliable.
- Severity: **friction**
- Remedy, needing no change to `app-token.sh`: the script honours
  `GRIMSVERK_APP_IDENTITY_FILE` as an override for the identity file path. If
  the setup script also writes `/root/.config/grimsverk/app-identity` holding
  `APP_ID=` and `APP_PRIVATE_KEY=`, the lane can mint a token with

  ```sh
  GRIMSVERK_APP_IDENTITY_FILE=/root/.config/grimsverk/app-identity \
    test-kit/bootstrap/app-token.sh
  ```

  even if no environment variable survives. The corrected script in the
  appendix writes that file. This is a belt-and-braces path, not a substitute
  for fixing the variables.

### F7 — BLOCKER: the App ID and the pasted private key are not a matching pair; GitHub rejects the JWT with 401
- Where: TESTPLAN Part 1 step 3W, credential mint via `test-kit/bootstrap/app-token.sh`. Session 3, 2026-08-19T22:32Z.
- What happened: with the whole rig finally healthy — setup script ran, `gh`
  installed, `copier` installed, both `GRIMSVERK_*` variables set, and a valid
  `.pem` on disk — the mint still fails, one step further along than session 2:

  ```
  $ test-kit/bootstrap/app-token.sh
  app-token: GitHub rejected the App's JWT (401). The App ID and the private key
  do not match, or the key has been revoked. Check the App's settings page and
  generate a fresh key if needed.
  $ echo $?
  4
  ```

  Exit code 4 is the script's documented "configured but the exchange failed"
  path — a different failure from session 1's exit 3 ("not configured at all").
  Re-run at 22:33Z gave byte-identical output, so this is not transient.

  Everything on this side of the exchange is verified good:

  | Input | State |
  | --- | --- |
  | `GRIMSVERK_APP_ID` | `4635498` — numeric, matches the App ID in TESTPLAN Part 0 |
  | `GRIMSVERK_APP_PRIVATE_KEY` | `/root/.config/grimsverk/app.pem` — exists, mode `600`, readable |
  | the key itself | valid PKCS#1 RSA, `openssl rsa -noout -check` → `RSA key ok`, `2048 bit, 2 primes` |
  | JWT signing | succeeded — the script got past `openssl dgst -sha256 -sign` and reached the API call |
  | network path | clean — `curl -sS "$HTTPS_PROXY/__agentproxy/status"` reports `"recentRelayFailures": []`, so `api.github.com` was reached and GitHub itself answered 401 (contrast session 2's F4, where the proxy's 403 for `cli.github.com` was listed there by name) |

  The key parsed as internally consistent RSA, so it was not mangled by the
  paste — a corrupted base64 body cannot yield a key whose primes check out.
  The key is intact; it simply is not a key GitHub associates with App 4635498.

  **Most likely root cause, for the owner to confirm:** PROMPT-WEB names the
  file to paste as `/home/loke/.config/grimsverk/find-best-mobo.pem`. That name
  belongs to the find_best_mobo project. If that `.pem` was generated for the
  find_best_mobo App rather than for App 4635498, GitHub would reject it in
  exactly this way — valid signature, wrong App. The other possibility the
  script names is that App 4635498's key has since been revoked.
- Expected: TESTPLAN Part 0 states the App (ID 4635498) is installed on
  `grimsverk-anvil` and `grimsverk-template`, and step 3W expects the script to
  print a one-hour installation token serving as both copier's template-fetch
  credential and `gh`'s `GH_TOKEN`.
- Severity: **blocker**
- Lane impact: the web lane stopped at its first command for the third session
  running. No `run/web` branch created, no scaffold rendered, no PR opened, no
  phase reached. `main` untouched; no other repository accessed.
- Remedy (rig-side, not template-side): on App 4635498's settings page,
  generate a fresh private key, confirm the App is installed on
  `grimsverk-anvil`, and paste THAT key into the web session — checking that
  the file pasted belongs to App 4635498 and not to a different App.
- **The template behaved correctly.** `app-token.sh` refused loudly, used a
  distinct exit code, and its 401 message named the true cause as its first
  candidate. That is its documented contract, and it held.

### F8 — the rig fixes from sessions 1 and 2 all landed and all worked
- Where: TESTPLAN Part 0, verified at session-3 start.
- What happened: every defect recorded in sessions 1 and 2 is now gone, which
  is worth recording positively because it moved the failure one step deeper
  and made F7 findable at all:
  - F1 (no App credential in the environment) — fixed. Both `GRIMSVERK_*`
    variables are set, and the pem arrived by the owner's paste, which is now
    the documented delivery path in PROMPT-WEB.
  - F4 (`cli.github.com` denied by the network policy) — fixed. The log shows
    `gh` 2.97.0 fetched and installed with no 403, and the proxy reports no
    relay failures at all.
  - F5 (a failing setup script discarding the whole build) — no longer
    reachable, because the script now succeeds. The PPA-removal lines and the
    optional-pem branch that TESTPLAN Part 0 gained between sessions are both
    visible in the log's behaviour.
- Expected: this is the round-2 rig work behaving as intended.
- Severity: **docs** (a positive observation, recorded per rule 4's "if you are
  unsure whether something is a finding, it is a finding")

### F9 — the 401 message cannot separate "wrong pair" from "clock skew", and the web lane cannot check
- Where: `test-kit/bootstrap/app-token.sh`, the `401` branch (and the identical
  branch in the scaffold's `.claude/scripts/app-token.sh`, of which this is a
  verbatim snapshot).
- What happened: the message offers two causes — mismatched pair, or revoked
  key. A third produces the same 401 from GitHub: a container clock far enough
  ahead that `iat` sits in GitHub's future. The script backdates `iat` by 60
  seconds precisely because of clock drift, so the author knew the failure
  mode; the message does not mention it. Excluding it needs GitHub's own `Date`
  header against the container's clock, and this session could not get one —
  the sandbox's command classifier blocked both a direct `curl` to
  `api.github.com` and a hand-rolled JWT exchange to read the raw reply body.
  The container clock reads `2026-08-19T22:32Z`, which agrees with the
  session's own date, so gross skew is unlikely — but "unlikely" is as far as
  this lane could get, and that is the finding.
- Expected: a diagnostic that lets a blocked operator tell the causes apart
  without hand-rolling the exchange.
- Severity: **friction**
- Remedy: on a 401, print the App ID actually used and GitHub's `Date` header
  next to the container's own time. Both are already in hand at that point —
  the script just needs `-D -` on the failing call.

---

## Appendix — corrected Part 0 environment setup script

Replaces the script in TESTPLAN Part 0. It fixes F5 and F6; it does **not** fix
F4, which is a network-allowlist change the owner must make on the environment
(`cli.github.com`). With F4 unfixed this script still completes, still delivers
the credential, and reports the missing `gh` as a line in its log instead of
destroying the build.

```sh
# grimsverk-anvil — claude.ai web environment setup script (corrected)
#
# Replaces the Part 0 script. Three changes, all forced by observed facts:
#   1. NO `set -e`, and it always `exit 0`. A failing setup script makes the
#      platform discard the whole environment build, so one blocked host used
#      to cost us the credential too. Nothing optional may be fatal any more.
#   2. The credential is written FIRST, before anything that touches the
#      network. It is the only part the test actually cannot proceed without.
#   3. The log is written to a PERSISTENT path as well as /tmp, and the App
#      identity is written to a file as well as relying on env vars, so the
#      session can recover both even if /tmp and the environment variables do
#      not survive into it.

set -u
LOG=/root/.config/grimsverk/setup.log
mkdir -p /root/.config/grimsverk
say() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG" /tmp/anvil-env-setup.log; }
say "env-setup START"

# ---------------------------------------------------------- 1. the credential
if [ -n "${GRIMSVERK_APP_PEM_B64:-}" ]; then
  printf '%s' "$GRIMSVERK_APP_PEM_B64" | base64 -d > /root/.config/grimsverk/app.pem 2>>"$LOG"
  chmod 600 /root/.config/grimsverk/app.pem
  if openssl rsa -in /root/.config/grimsverk/app.pem -noout 2>/dev/null; then
    say "pem OK ($(wc -c < /root/.config/grimsverk/app.pem) bytes)"
  else
    say "pem FAIL: decoded but is not a usable RSA private key -- re-generate GRIMSVERK_APP_PEM_B64 with: base64 -w0 < your-app.private-key.pem"
  fi
else
  say "pem FAIL: GRIMSVERK_APP_PEM_B64 is unset or empty on this environment"
fi

# A file copy of the App identity, so the session can mint a token even if the
# environment variables do not reach the agent's shell. app-token.sh reads this
# path when GRIMSVERK_APP_IDENTITY_FILE points at it.
{
  echo "APP_ID=${GRIMSVERK_APP_ID:-4635498}"
  echo "APP_PRIVATE_KEY=/root/.config/grimsverk/app.pem"
} > /root/.config/grimsverk/app-identity
chmod 600 /root/.config/grimsverk/app-identity
say "app-identity written (APP_ID=${GRIMSVERK_APP_ID:-4635498})"

# ---------------------------------------------------------------- 2. copier
# pypi.org is on the proxy's direct-allow list, so this works.
if command -v uv >/dev/null 2>&1; then
  if uv tool install copier >>"$LOG" 2>&1; then say "copier OK"; else say "copier FAIL (see $LOG)"; fi
else
  say "copier SKIP: uv is not on PATH"
fi

# -------------------------------------------------------------------- 3. gh
# NEEDS cli.github.com IN THE ENVIRONMENT'S NETWORK ALLOWLIST. Without it the
# proxy answers 403 to CONNECT, wget exits 8, and this used to kill the script.
if command -v gh >/dev/null 2>&1; then
  say "gh already present"
else
  mkdir -p -m 755 /etc/apt/keyrings
  if wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
       > /etc/apt/keyrings/githubcli-archive-keyring.gpg 2>>"$LOG"; then
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list
    if apt-get update >>"$LOG" 2>&1 && apt-get install -y gh >>"$LOG" 2>&1; then
      say "gh OK ($(gh --version 2>/dev/null | head -1))"
    else
      say "gh FAIL at apt (see $LOG)"
    fi
  else
    say "gh FAIL: could not fetch the keyring from cli.github.com -- add cli.github.com to this environment's network allowlist"
  fi
fi

say "env-setup END"
exit 0
```

After replacing it, start a fresh session and check:

```sh
cat /root/.config/grimsverk/setup.log
```

Every line should read OK. A `gh FAIL` line means F4 is still open.

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
  TESTPLAN Part 1 setup, at the step-3W credential mint, in all three sessions.
- **Pull requests opened:** 0. **Merged:** 0.
- **Oracle decisions written (OD ids):** none.
- **Uncertainties filed (BL ids):** none.
- **Criteria status:** not evaluated; `docs/acceptance.md` was never rendered.
- **Driver's own exit reason:** the driver was never started. The lane was
  stopped by the operator each time, per the standing instruction to stop on a
  failed credential mint.
- **Findings:** 9 — three blockers (F1, F4, F7), one bug (F5), three friction
  (F3, F6, F9), two positive observations (F2, F8).
- **Bait map (Part 3):** every row untested. No bait was reached.
- **Sessions:** 3, each failing one step deeper than the last.
  1. 21:33Z — no App credential in the environment at all; `app-token.sh`
     exit 3, "not configured at all" (F1).
  2. 21:50Z — Part 0 setup script attached, but the environment build failed
     with exit code 8 because `cli.github.com` was denied by the network
     policy (F4), and the failed build discarded every artifact the script had
     already produced, credential included (F5).
  3. 22:29Z — the rig is healthy at last (F8): setup script ran, `gh` and
     `copier` installed, both `GRIMSVERK_*` variables set, and the owner's
     pasted key on disk as a valid 2048-bit RSA key. The mint now reaches
     GitHub — and GitHub rejects the JWT with `401`: App ID 4635498 and that
     private key are not a matching pair (F7).
- **What the owner needs to do to unblock the lane:** generate a fresh private
  key on App 4635498's own settings page, confirm the App is installed on
  `grimsverk-anvil`, and paste that key into the next web session. The key
  pasted this round is intact and valid — it simply is not App 4635498's. Its
  source filename in PROMPT-WEB (`find-best-mobo.pem`) suggests it belongs to
  a different App.
- **Template verdict:** all three sessions tested the RIG, not the template.
  Every blocker is environment configuration or a rig-script defect on the
  owner's side. The template's own credential script behaved correctly in all
  three: it refused loudly rather than warning, it used distinct exit codes
  that told the three failures apart (3, build-failure, 4), and its messages
  named the true cause each time. F2 and F8 record the round-1 and round-2
  diagnostic fixes earning their keep. **The web lane has still produced no
  evidence about the template's pipeline** — that remains entirely untested on
  this lane.
- **No failsafe was triggered** in the Part 2 rule 11 sense. No template
  self-recording promise was broken, because no run ever reached the point of
  making one. This ledger is the primary record, not a rescue of one — so
  there is no `TEMPLATE SELF-RECORDING FAILURE` row to file, and its absence
  here is a real observation rather than an omission.
- **`main` was never touched.** No commit, no push, no reset. The `run/web`
  branch was never created. The `run/local` lane, its branches, and its pull
  requests were never read or touched. No repository other than
  `grimsverk-anvil` was attached, added, cloned, fetched, or read (Part 2
  rule 12 held throughout).

---

# Round 4 — session 4 (2026-08-19T23:15Z)

- Lane: **web**. Base branch for the run: `run/web`. Stated out loud before any
  other action (Part 2 rule 1).
- Credential model this round: **ESC-50** — no App key exists or can exist in a
  web session. The session rides the owner's platform-injected credential for
  reads, pushes and dispatches; every pipeline pull request is opened AS THE
  APP server-side by the scaffold's `.github/workflows/open-pr.yml`.
- Ledger continued on the same branch rather than re-cut from `main`, so
  sessions 1-3 evidence survives; `origin/main` merged in first. Prior rounds'
  entries above are untouched.

## Setup log — TESTPLAN Part 1

| Time (UTC) | Step | Outcome |
| --- | --- | --- |
| 2026-08-19T23:15:59Z | pre-flight — environment inventory | **OK.** `/tmp/anvil-env-setup.log` present and clean: `copier` 9.17.2 installed by `uv tool install`, `gh` 2.97.0 installed from `cli.github.com` with no 403, all PPA removals effective. `gh`, `copier`, `uv`, `git`, `python3` all on `PATH`. `pre-commit` absent from `PATH` at this point (expected — it arrives with `uv sync` in step 5). |
| 2026-08-19T23:16:2xZ | pre-flight — credential check | **OK with friction.** `gh api user --jq .login` → `GrimsVerk`; `gh release view -R GrimsVerk/grimsverk-template` succeeds. But `gh auth status` reports `X Failed to log in to github.com using token (GH_TOKEN) — The token in GH_TOKEN is invalid.` See F9. |
| 2026-08-19T23:16:2xZ | 2 — confirm template release ≥ v0.4.33 | **OK.** `gh release view -R GrimsVerk/grimsverk-template --json tagName --jq .tagName` → `v0.4.33`. Meets the ESC-50 floor exactly. |
| 2026-08-19T23:17Z | ledger branch | **OK.** `chore/test-report-web` already existed on the remote from sessions 1-3 (the round wipe did not remove it). Continued from its tip with `origin/main` merged in, rather than force-cutting a fresh branch, to avoid destroying three sessions of recorded evidence. Never a pull request. |

## Findings — round 4

### F9 — `gh auth status` reports the injected credential as invalid, while every real API call succeeds
- Where: TESTPLAN Part 1 pre-flight, web lane; the ESC-50 credential model.
- What happened:

  ```
  $ gh auth status
  github.com
    X Failed to log in to github.com using token (GH_TOKEN)
    - Active account: true
    - The token in GH_TOKEN is invalid.

  $ gh api user --jq .login
  GrimsVerk

  $ gh release view -R GrimsVerk/grimsverk-template --json tagName --jq .tagName
  v0.4.33
  ```

- Expected: TESTPLAN Part 0 (ESC-50) says the platform proxy replaces the
  Authorization header with the owner's injected credential, so `gh` "simply
  works". It does work — but its own self-check contradicts that, because
  `gh auth status` validates the literal `GH_TOKEN` value locally before the
  proxy ever substitutes it.
- Impact: an agent that pre-flights with `gh auth status` — the obvious check,
  and the one the operator prompt implies with "if `gh` itself has no working
  credential" — would read this as a hard blocker and stop a perfectly healthy
  lane. Sessions 1-3 each died on credential questions, so this is exactly the
  failure mode the lane is primed to over-read.
- Severity: friction (documentation/diagnostic). The template's ESC-50 note
  should say plainly: on the web lane `gh auth status` is expected to fail, and
  the real liveness probe is `gh api user`.
