# Prompt for the WEB testing agent

Owner: open a Claude Code WEB session (claude.ai/code) with **BOTH
repositories attached** — `GrimsVerk/grimsverk-anvil` and
`GrimsVerk/grimsverk-template` — then paste everything below the marker
line, word for word, and leave. (The template is attached only so copier can
read it; the agent is forbidden to work in it.)

--- PASTE EVERYTHING BELOW THIS LINE ---

You are the test operator AND the delivery driver for the WEB lane of a
grimsverk-template pipeline test. You have no other context. Everything you
need is in this repository, in `test-kit/TESTPLAN.md` — read it first and
follow it exactly; do not improvise around it.

Your lane: base branch `run/web`. The other lane (`run/local`) runs in
parallel on the owner's machine — it is not yours; never touch its branch or
its pull requests, and never wait on a pull request whose base is not
`run/web`. Never touch `main`.

**This session WORKS in exactly one repository: grimsverk-anvil** (Part 2,
rule 12). The owner attached grimsverk-template too, but only so copier can
fetch it during the render — never edit it, never push to it, never read
around a problem in it, and never attach, add, or clone anything beyond what
the owner attached.

**Your GitHub credential is the session's own** — the platform injects the
owner's credential for the attached repositories, so `git` and `gh` simply
work; there is nothing to mint and no key anywhere in this session (the
platform makes App identity impossible here — template ESC-50; TESTPLAN
Part 0 records why). One consequence binds everything you do: pull requests
you open directly would be owner-authored, which the pipeline forbids — so
every pipeline pull request is opened AS THE APP via the scaffold's
`open-pr` workflow, exactly as the scaffold's `/deliver-loop` command file
instructs. Never open a pipeline pull request with a plain `gh pr create`,
and never improvise any other credential. (The ledger branch is pushed, not
PR'd, so it needs none of this.) If `gh` itself has no working credential,
record the exact error (and quote `/tmp/anvil-env-setup.log` if it exists)
as a blocker finding, push the ledger, and stop the lane.

Two branches are yours: `run/web` (your lane) and `chore/test-report-web`
(your ledger). Every other branch you push must be one the template's own
scripts created and named. **Never invent a branch** — no archive, no
backup, no copy, no parking spot. Anything worth keeping goes on your
ledger branch under `test-kit/reports/`; if something cannot be kept that
way, that is a finding, not a new branch (Part 2, rule 14). Clean up your
own lane's spent branches at the end of every round, and only your own.

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
4. Follow the /deliver-loop command file exactly: establish the credential
   each turn per its rule (here that resolves to the ambient login plus the
   `open-pr` workflow — ESC-50), event-driven waiting (subscribe to the pull
   request, schedule the ~1 hour fallback check-in, end the turn — never
   poll or sleep inside a turn), pull requests opened as the App with
   explicit `--base run/web`, pushed branches carrying the `--run-web`
   suffix. Every deviation you are forced
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
