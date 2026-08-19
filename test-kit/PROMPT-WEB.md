# Prompt for the WEB testing agent

Owner: open a Claude Code WEB session (claude.ai/code) on
`GrimsVerk/grimsverk-anvil` and paste everything below the marker line, word
for word.

--- PASTE EVERYTHING BELOW THIS LINE ---

You are the test operator AND the delivery driver for the WEB lane of a
grimsverk-template pipeline test. You have no other context; everything you
need is in this repository.

Your lane: base branch `run/web`, driven by the `/deliver-loop` command in
this session. The other lane (`run/local`) runs in parallel on the owner's
machine — it is not yours; never touch its branches or pull requests, and
never wait on a pull request whose base is not `run/web`.

Do this, in order:

1. Read `test-kit/TESTPLAN.md` — Part 2 (rules for testing agents) binds you.
   Read the project's `AGENTS.md` and `GLOSSARY.md`. State your lane out loud.
2. Preflight, and record any failure as a finding: `gh auth status` works in
   this container; `.claude/scripts/app-token.sh >/dev/null` succeeds; branch
   `run/web` exists on origin. If `gh` or the App identity is missing, the
   environment was not prepared — record the exact error as a blocker finding,
   push the ledger, tell the owner, and stop this lane. Do not install or
   improvise credentials beyond what the environment already provides.
3. Start your findings ledger at `test-kit/reports/web.md` on branch
   `chore/test-report-web`, per TESTPLAN Part 2 rule 4. First entry: the
   preflight results.
4. Switch the checkout to `run/web`. Then run the project's `/deliver-loop`
   command with the scope argument `base: run/web`. When it asks for limits,
   these are the owner's numbers, given here in advance: maximum 30 pull
   requests, maximum 12 wall-clock hours, maximum 60 iterations. The command
   file is expected to say that no usage gauge is reachable in a web session
   and to ask for countable limits — record it as a finding if it behaves any
   other way (TESTPLAN Part 2, rule 8).
   The run must establish and announce `run/web` as its base branch on the
   first turn. If it ever reports a base other than `run/web`, or the detector
   hands you a pull request targeting a different base, stop the run and
   record a blocker finding.
5. Follow the /deliver-loop command file exactly: event-driven waiting
   (subscribe to the pull request, schedule the ~1 hour fallback check-in, end
   the turn — never poll or sleep inside a turn), pull requests opened as the
   GitHub App with explicit `--base run/web`, and pushed branches carrying the
   `--run-web` suffix. Every deviation you are forced into is a finding.
   Update the ledger with every PHASE transition (TESTPLAN rule 5) and every
   observation-checklist item (TESTPLAN rules 9 and 10: branch deletion after
   each merge, auto-merge arming, App authorship, per-check durations,
   cross-lane updates), committing and pushing as you go — this container can
   be reclaimed between turns, so an unpushed ledger line is a lost ledger
   line.
6. When the run stops (done, limit, pattern, refusal — any documented stop),
   the driver machinery lands its own run evidence; you additionally write the
   summary block into your ledger (TESTPLAN rule 6), push
   `chore/test-report-web`, and report to the owner: high level, per the
   glossary rules — what stopped the run, which phases ran, how many pull
   requests merged, and your top findings. Do not restart the run.

Remember throughout: you are testing the template, not the product. Every
surprise, unclear message, wrong doc, or workaround is a finding for the
ledger. If a template bug blocks the lane, record it and stop; never edit
`.github/`, `.claude/`, `AGENTS.md`, or any gate to get unstuck.
