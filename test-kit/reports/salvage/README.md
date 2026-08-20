# Salvage — six orphaned web-lane branches, preserved here

Six branches of this lane held content that existed **nowhere else**: four
run-evidence branches whose pull requests were closed rather than merged, and
two oracle branches from a round whose lane base was later rebuilt, so their
commits are no longer reachable from `run/web`.

They could not be cleaned up in place. A hosted session is refused ref deletion
by its egress proxy — `git push --delete` and `DELETE /git/refs/heads/…` both
answer 403 while branch **creation** succeeds — which is why every orphan in
this repository belonged to the web lane and none to the local one. That is
this lane's F34 and template ESC-78.

Merging them into this branch was considered and rejected: their merge base is
the lane's scaffold, so a merge would drag the whole generated project onto a
ledger branch that deliberately carries only `test-kit/`. The content is copied
instead, unchanged apart from the redaction below, which makes the branches
safe for the owner to delete by hand.

| Directory | Came from | What it is |
| --- | --- | --- |
| `run-20260819T231559Z/` | `docs/run-20260819T231559Z--run-web` | run evidence |
| `run-20260819T233920Z/` | `docs/run-20260819T233920Z--run-web` | run evidence |
| `run-20260820T013038Z/` | `docs/run-20260820T013038Z--run-web` | run evidence |
| `run-20260820T022911Z/` | `docs/run-20260820T022911Z--run-web` | run evidence |
| `oracle-20260820013147/` | `docs/oracle-20260820013147--run-web` | an oracle ruling on ESC-1 / BL-3 / BL-4, from a round whose base was rebuilt |
| `oracle-20260820022922/` | `docs/oracle-20260820022922--run-web` | the same ruling, re-derived the next round |

**One redaction, per Part 2 rule 13.** Two worker logs carried an absolute
`/home/<name>` path — a session container's, not the owner's machine — and it
is replaced by `<home>`. Every other byte is as it was on the branch.

Nothing here is a new finding. It is the raw material behind entries already in
`web.md`, kept because a closed pull request's branch is often the only copy of
what it carried.
