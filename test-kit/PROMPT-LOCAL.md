# Prompt for the LOCAL testing agent

Owner: open a Claude Code session on your machine (any directory) and paste
everything below the marker line, word for word.

--- PASTE EVERYTHING BELOW THIS LINE ---

You are the test operator for the LOCAL lane of a grimsverk-template pipeline
test. You have no other context. Everything you need is in the repository
`GrimsVerk/grimsverk-anvil`, in `test-kit/TESTPLAN.md` — read it first and
follow it exactly; do not improvise around it.

Your lane: base branch `run/local`. The other lane (`run/web`) runs in
parallel in a web session — it is not yours; never touch its branch or its
pull requests. Never touch `main`. State your lane out loud before anything
else.

The App ID 4635498 and the key path
/home/loke/.config/grimsverk/find-best-mobo.pem are ready for you.

Do this, in order:

1. Read `test-kit/TESTPLAN.md` in full. Part 1 is YOUR setup — you do all of
   it yourself, for the `run/local` lane, on the `run/local` branch: clone,
   branch off `main`, render the scaffold with copier, install the canned
   inputs, toolchain-then-commit, push, and the local-only rig duties (the
   ruleset reset, the App identity file — use the App ID and key path given
   above — and gating BOTH lanes once both exist). Part 2 binds you
   throughout. Work out the exact commands from the plan; if the plan and
   reality disagree, that is a finding, not a licence to improvise.
2. Start your findings ledger at `test-kit/reports/local.md` on branch
   `chore/test-report-local` (branched off `main`, pushed, never a pull
   request), per Part 2 rule 4. First entries: each setup step's outcome,
   including every wait, retry, and surprise — setup friction is test data.
3. Once TESTPLAN Part 1 step 7 is green (the full readiness check passes for
   `run/local`), read the scaffold's `AGENTS.md` and `GLOSSARY.md` — they
   exist now — then start the driver in the background, logging to a file:

       git switch run/local
       nohup .claude/scripts/deliver-loop.sh --base run/local \
         --budget-points 8 --max-prs 30 --max-hours 12 \
         > /tmp/anvil-local-driver.log 2>&1 &

   The driver must announce `THIS RUN'S BASE BRANCH: run/local`. If it
   announces anything else, kill it immediately and record a blocker finding.
   If it refuses to start (readiness, identity, budget), record the refusal
   verbatim as a finding and stop — do not force it.

   **The weekly rate-limit budget is the primary limit of this lane and is
   itself under test** (Part 2, rule 8). The start banner must show a real
   gauge reading ("budget: weekly at N%…"). If it reports no reachable gauge,
   that is a blocker finding: record it and stop — do not let the run proceed
   on the PR/hour backstops alone.
4. Monitor without interfering: every 10–15 minutes read the tail of
   `/tmp/anvil-local-driver.log` and `.claude/deliver-loop/run.md`, and note
   every new PHASE line in your ledger (Part 2 rule 5) plus every item the
   observation checklist demands (rules 9 and 10: branch deletion after each
   merge, auto-merge arming, App authorship, per-check durations, budget
   lines, cross-lane updates). Use your environment's background-wait
   mechanisms; never busy-loop. Do not kill the driver unless the log has
   been completely silent for more than 90 minutes — if you do, that is
   itself a finding.
5. When the driver stops (any exit code), secure the evidence before anything
   else:
   - Copy the raw driver log into the ledger branch:
     `cp /tmp/anvil-local-driver.log test-kit/reports/local-driver.log`,
     commit, push.
   - If the driver died WITHOUT landing its report (a kill, a crash — the
     buffer `.claude/deliver-loop/run.md` still has content), land it:
     `.claude/scripts/deliver-loop.sh --base run/local --land-evidence`
   - Verify the driver landed `docs/runs/<timestamp>/` (report, `reviews/`,
     `workers/`) and opened its evidence pull request, and that it can merge.
     If anything failed, paste the report's content into your ledger — the
     ledger branch is the one path no gate can block.
   - **Every failsafe you had to use gets its own finding, titled
     `TEMPLATE SELF-RECORDING FAILURE: <what>` (Part 2, rule 11).** Needing
     `--land-evidence`, a missing report, missing `reviews/` or `workers/`,
     an evidence PR that never opened or cannot merge — each means the
     template failed to record its own failure, which is exactly what must be
     reported upstream. The raw-log copy alone is routine — unless the raw
     log turns out to be the ONLY surviving record, in which case it is not.
6. Write the summary block into the ledger (Part 2 rule 6), push
   `chore/test-report-local`, and report to the owner: high level, per the
   glossary rules — what stopped the run, which phases ran, how many pull
   requests merged, and your top findings. Do not restart the run.

Remember throughout: you are testing the template, not the product. Every
surprise, unclear message, wrong doc, wait, or workaround is a finding for
the ledger. If a template bug blocks the lane, record it and stop; never edit
`.github/`, `.claude/`, `AGENTS.md`, or any gate to get unstuck.
