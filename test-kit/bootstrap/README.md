# Bootstrap tools

`app-token.sh` is a **verbatim snapshot** of the template's
`.claude/scripts/app-token.sh` (v0.4.31). It exists for exactly one gap: the
web lane needs an App-minted token BEFORE the scaffold (and with it the real
script) has been rendered — to give `gh` a credential and to let copier fetch
the private template. It reads `GRIMSVERK_APP_ID` and
`GRIMSVERK_APP_PRIVATE_KEY` from the environment, resolves the repository from
the git remote, and prints a one-hour installation token on stdout.

Once the scaffold exists on your lane, use the real
`.claude/scripts/app-token.sh` and never this copy again. If the two ever
disagree, the scaffold's version is the truth and the disagreement is a
finding (this snapshot is not updated by `copier update`).
