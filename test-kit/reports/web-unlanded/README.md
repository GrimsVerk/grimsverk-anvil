# Web lane — evidence that never landed on a pull request

These files were produced by the template's own machinery on branches whose
pull requests were closed unmerged when the owner restarted the round. The
branches still exist on the remote and cannot be deleted from a hosted session
(see the ledger's F34), so this directory is the durable copy — on the ledger
branch, under `test-kit/reports/`, per TESTPLAN Part 2 rule 14. **No branch was
invented to hold it.**

| File | Source branch | Why it is here |
| --- | --- | --- |
| `run-20260820T013038Z.md` | `docs/run-20260820T013038Z--run-web` | Round 3's run report. Its pull request (#9) was opened by the App and closed unmerged at the round 3.1 restart, so this report never reached `run/web`. |
| `run-20260820T022911Z.md` | `docs/run-20260820T022911Z--run-web` | Round 3.1's run report. Same story — closed at the round 3.2 restart. |
| `worker-oracle-20260820022922.log` | same | The one worker log collected for round 3.1, kept because `workers/` collection (ESC-42) is on the observation checklist and this is its round-3.1 sample. |

Not copied, and why:

- **Round 4 and round 2.1 run reports** — already pasted verbatim into the
  ledger itself, under findings F14 and F20, because their evidence pull
  requests could not be opened at all. Copying them again would duplicate.
- **The two `docs/oracle-*--run-web` branches** — they carry rounds 3 and 3.1
  oracle rulings, which are near-identical to OD-1 … OD-3 as finally merged to
  `run/web` in round 3.2 (`docs/DESIGN.oracle.md`). Superseded by landed work,
  so the landed copy is the record.
- **The `MISSING.md` review markers** — their content and cause are already
  characterised in the ledger (F19, F25); the markers themselves carry no
  payload, which is the whole point of them.
