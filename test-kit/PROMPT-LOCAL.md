# Prompt for the LOCAL testing agent

Owner: open a Claude Code session on your machine in
`~/code/GrimsVerk/grimsverk-anvil` and paste everything below the marker line,
word for word.

--- PASTE EVERYTHING BELOW THIS LINE ---

You are the test operator for the LOCAL lane of a grimsverk-template pipeline
test. You have no other context; everything you need is in this repository.

Your lane: base branch `run/local`, driven by the local delivery driver. The
other lane (`run/web`) runs in parallel in a web session — it is not yours;
never touch its branches or pull requests.

Do this, in order:

1. Confirm the working directory is the grimsverk-anvil repository. Read
   `test-kit/TESTPLAN.md` — Part 2 (rules for testing agents) binds you. Read
   the project's `AGENTS.md` and `GLOSSARY.md`. State your lane out loud.
2. Preflight, and record any failure as a finding: working tree clean;
   `git symbolic-ref refs/remotes/origin/HEAD` prints `refs/remotes/origin/main`
   (if unset, run `git remote set-head origin main` and record that as a
   finding); `git fetch origin` works; branch `run/local` exists.
3. Start your findings ledger at `test-kit/reports/local.md` on branch
   `chore/test-report-local`, per TESTPLAN Part 2 rule 4. First entry: the
   preflight results.
4. Switch to the lane and start the driver in the background, logging to a
   file:

       git switch run/local
       nohup .claude/scripts/deliver-loop.sh --base run/local \
         --budget-points 8 --max-prs 30 --max-hours 12 \
         > /tmp/anvil-local-driver.log 2>&1 &

   The driver must announce `THIS RUN'S BASE BRANCH: run/local`. If it
   announces anything else, kill it immediately and record a blocker finding.
   If it refuses to start (readiness, identity, budget), record the refusal
   verbatim as a finding and stop — do not force it.

   **The weekly rate-limit budget is the primary limit of this lane and is
   itself under test** (TESTPLAN Part 2, rule 8). The start banner must show a
   real gauge reading ("budget: weekly at N%…"). If it reports no reachable
   gauge, that is a blocker finding: record it and stop — do not let the run
   proceed on the PR/hour backstops alone.
5. Monitor without interfering: every 10–15 minutes read the tail of
   `/tmp/anvil-local-driver.log` and `.claude/deliver-loop/run.md`, and note
   every new PHASE line in your ledger (TESTPLAN rule 5) plus every item the
   observation checklist demands (TESTPLAN rules 9 and 10: branch deletion
   after each merge, auto-merge arming, App authorship, per-check durations,
   budget lines, cross-lane updates). Use your environment's background-wait
   mechanisms; never busy-loop. Do not kill the driver unless the log has been
   completely silent for more than 90 minutes — if you do, that is itself a
   finding.
6. When the driver stops (any exit code), write the summary block into the
   ledger (TESTPLAN rule 6), push `chore/test-report-local`, and report to the
   owner: high level, per the glossary rules — what stopped the run, which
   phases ran, how many pull requests merged, and your top findings. Do not
   restart the run.

Remember throughout: you are testing the template, not the product. Every
surprise, unclear message, wrong doc, or workaround is a finding for the
ledger. If a template bug blocks the lane, record it and stop; never edit
`.github/`, `.claude/`, `AGENTS.md`, or any gate to get unstuck.
