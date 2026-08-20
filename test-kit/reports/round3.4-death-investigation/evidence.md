# Round 3.4 death — raw investigation evidence

## The two command lines, byte-identical
```
# find_best_mobo's driver, pid 483772, cwd <home>/code/GrimsVerk/find_best_mobo
bash .claude/scripts/deliver-loop.sh --base run/local --budget-points 20 --max-prs 30 --max-hours 12 
# this lane's driver, as launched (round 3.4)
bash .claude/scripts/deliver-loop.sh --base run/local --budget-points 20 --max-prs 30 --max-hours 12
```

## Concurrent processes at investigation time
```
 483772       02:58 bash .claude/scripts/deliver-loop.sh --base run/local --budget-points 20 --max-prs 30 --ma
 486795       02:44 timeout 3600 .claude/scripts/spawn-worker.sh --id steward-od-8 --role steward --engine cla
 486796       02:44 bash .claude/scripts/spawn-worker.sh --id steward-od-8 --role steward --engine claude --ba
 488571       00:00 /usr/bin/bash -c source <home>/.claude/shell-snapshots/snapshot-bash-1787174881278-zbv
 488606       00:00 /usr/bin/bash -c source <home>/.claude/shell-snapshots/snapshot-bash-1787174881278-zbv
pid 483772 cwd: <home>/code/GrimsVerk/find_best_mobo
pid 486795 cwd: <home>/code/GrimsVerk/find_best_mobo
pid 486796 cwd: <home>/code/GrimsVerk/find_best_mobo
```

## Negative results (each checked, each clean)
```
coredumps:        No coredumps found.
kernel OOM:       none in journalctl -k for the window
systemd-oomd:     active, but no kill logged for the window
disk:             /dev/mapper/root  1.9T   66G  1.8T   4% /home
memory:           Mem:            31Gi       9.6Gi        14Gi       327Mi       8.7Gi        21Gi
engine:           2.1.233 (Claude Code)
auth:             loggedIn=true, claude.ai, firstParty
budget at probe:  session=21 week=10 week_model=9
```

## Dead worker session transcript — 8 entries, no assistant turn
```
prompt delivered 2026-08-20T11:10:20.158Z; entry types:
queue-operation, queue-operation, user, attachment x3, last-prompt, ai-title
no assistant entry, no error entry, no API response of any kind
```
