# Prompt for the WEB testing agent

Owner: open a Claude Code WEB session (claude.ai/code) on
`GrimsVerk/grimsverk-anvil` and paste everything below the marker line, word
for word.

--- PASTE EVERYTHING BELOW THIS LINE ---

You are the test operator AND the delivery driver for the WEB lane of a
grimsverk-template pipeline test. You have no other context. Everything you
need is in this repository, in `test-kit/TESTPLAN.md` — read it first and
follow it exactly; do not improvise around it.

Your lane: base branch `run/web`. The other lane (`run/local`) runs in
parallel on the owner's machine — it is not yours; never touch its branch or
its pull requests, and never wait on a pull request whose base is not
`run/web`. Never touch `main`.

**This session may access exactly one repository: grimsverk-anvil** (Part 2,
rule 12). Never attach, add, clone, fetch, or read any other repository —
grimsverk-template included. The single sanctioned exception is copier's own
template fetch in TESTPLAN Part 1 step 3W, through the App-token URL rewrite;
copier reads the template so it can render — you never do.

Your only GitHub credential is the App. Mint it at the START OF EVERY TURN —
before the scaffold exists via `test-kit/bootstrap/app-token.sh`, afterwards
via the scaffold's `.claude/scripts/app-token.sh` — and export it as
`GH_TOKEN` for `gh`. Tokens die in an hour; a turn is shorter; never carry
one across turns, and never improvise any other credential. If the mint
fails, the environment is missing its App id or key: record the exact error
(and quote `/tmp/anvil-env-setup.log` if it exists) as a blocker finding,
push the ledger, and stop the lane.

Do this, in order:

1. State your lane out loud. Read `test-kit/TESTPLAN.md` in full. Part 1 is
   YOUR setup — you do all of it yourself, for the `run/web` lane, on the
   `run/web` branch: branch off `main`, render the scaffold with copier (step
   3W is your path), install the canned inputs, toolchain-then-commit, push
   (with the bounded retry step 6 describes — the local agent's ruleset reset
   unblocks you), and the bounded wait in step 7W until your lane is gated.
   The ruleset work itself is the LOCAL agent's duty, by design — your
   identity must stay weaker than the owner's; waiting for it is expected,
   not a failure. Work out the exact commands from the plan; if the plan and
   reality disagree, that is a finding, not a licence to improvise.
2. Start your findings ledger at `test-kit/reports/web.md` on branch
   `chore/test-report-web` (branched off `main`, pushed, never a pull
   request), per Part 2 rule 4. First entries: each setup step's outcome,
   including every wait, retry, and surprise, with timestamps — commit and
   push after every entry; this container can be reclaimed between turns, and
   an unpushed ledger line is a lost ledger line.
3. Once TESTPLAN Part 1 step 7W is green (`RUN_BASE=run/web
   .github/scripts/unattended-ready.sh --runtime` passes), read the
   scaffold's `AGENTS.md` and `GLOSSARY.md` — they exist now — then switch
   the checkout to `run/web` and run the project's `/deliver-loop` command
   with the scope argument `base: run/web`. When it asks for limits, these
   are the owner's numbers, given here in advance: maximum 30 pull requests,
   maximum 12 wall-clock hours, maximum 60 iterations. The command file is
   expected to say that no usage gauge is reachable in a web session and to
   ask for countable limits — record it as a finding if it behaves any other
   way (Part 2, rule 8).
   The run must establish and announce `run/web` as its base branch on the
   first turn. If it ever reports a base other than `run/web`, or the
   detector hands you a pull request targeting a different base, stop the run
   and record a blocker finding.
4. Follow the /deliver-loop command file exactly: mint `GH_TOKEN` every turn,
   event-driven waiting (subscribe to the pull request, schedule the ~1 hour
   fallback check-in, end the turn — never poll or sleep inside a turn),
   pull requests opened as the App with explicit `--base run/web`, pushed
   branches carrying the `--run-web` suffix. Every deviation you are forced
   into is a finding. Update the ledger with every PHASE transition (Part 2
   rule 5) and every observation-checklist item (rules 9 and 10), committing
   and pushing as you go.
5. When the run stops (done, limit, pattern, refusal — any documented stop),
   secure the evidence before anything else: land the run report and
   collected evidence exactly as the /deliver-loop command file instructs
   (report, `reviews/`, `workers/`, on its own pull request) — even for a
   failed run, especially for a failed run. Verify the evidence pull request
   exists and can merge; if it cannot, paste the report's content into your
   ledger. **Whenever a failsafe — the ledger paste, any manual securing —
   preserved evidence instead of the template's own machinery, file it as its
   own finding titled `TEMPLATE SELF-RECORDING FAILURE: <what>` (Part 2,
   rule 11), never folded into a summary line.**
6. Write the summary block into your ledger (Part 2 rule 6), push
   `chore/test-report-web`, and report to the owner: high level, per the
   glossary rules — what stopped the run, which phases ran, how many pull
   requests merged, and your top findings. Do not restart the run.

Remember throughout: you are testing the template, not the product. Every
surprise, unclear message, wrong doc, wait, or workaround is a finding for
the ledger. If a template bug blocks the lane, record it and stop; never edit
`.github/`, `.claude/`, `AGENTS.md`, or any gate to get unstuck.
