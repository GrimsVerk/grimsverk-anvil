#!/usr/bin/env bash
#
# check-ledger.sh — run this BEFORE every push of a ledger branch.
#
#     test-kit/check-ledger.sh <lane>        # lane is 'local' or 'web'
#
# Two things it refuses, and both have already happened in this test bed.
#
# 1. A LOST FINDING. The ledger is the only record of the whole exercise and it
#    has no CI: it is pushed straight to `chore/test-report-<lane>` with no pull
#    request, deliberately, so nothing but this script stands between a careless
#    rewrite and a finding nobody can get back. Every `### F<n>` heading that
#    exists on the remote must still exist here, spelled the same.
#
# 2. A REGISTER VALUE (Part 2 rule 13). This repository is public. Machine
#    paths, home directories, SSH host aliases, usernames and the app id must
#    never appear in anything pushed — and they got in twice: once quoted as
#    evidence inside a finding, once in a copy of the kit that predated the
#    rule. Values are read from the owner's register when it exists, and the
#    generic shapes are checked always, because the web lane has no register
#    and still managed to leak a home path.
#
# It reads; it changes nothing. Exit 0 clean, 1 refused, 2 cannot ask.
set -uo pipefail

LANE="${1:-}"
case "$LANE" in
  local|web) ;;
  *) echo "check-ledger: usage: test-kit/check-ledger.sh <local|web>" >&2; exit 2 ;;
esac

git rev-parse --git-dir >/dev/null 2>&1 \
  || { echo "check-ledger: not inside a git repository" >&2; exit 2; }

BRANCH="chore/test-report-$LANE"
LEDGER="test-kit/reports/$LANE.md"
[[ -f "$LEDGER" ]] || { echo "check-ledger: $LEDGER does not exist here" >&2; exit 2; }

fail=0
say()  { echo "  $1"; }
bad()  { echo "  REFUSED  $1"; fail=1; }

echo "check-ledger: $LEDGER against origin/$BRANCH"

# ---------------------------------------------------------- 1. nothing lost
if git fetch -q origin "$BRANCH" 2>/dev/null \
   && git rev-parse -q --verify FETCH_HEAD >/dev/null 2>&1; then
  BEFORE="$(git show "FETCH_HEAD:$LEDGER" 2>/dev/null | grep -oE '^### F[0-9]+' | sort -u)"
  AFTER="$(grep -oE '^### F[0-9]+' "$LEDGER" | sort -u)"
  LOST="$(comm -23 <(printf '%s\n' "$BEFORE") <(printf '%s\n' "$AFTER") | tr -d ' ' | tr '\n' ' ')"
  if [[ -n "${LOST// /}" ]]; then
    bad "these findings are on the remote and NOT in your file: $LOST"
    say "         The ledger is append-only. Add a correction as a NEW entry;"
    say "         never delete or renumber one that is already pushed."
  else
    say "ok       every pushed finding is still here ($(wc -l <<<"$AFTER" | tr -d ' ') total)"
  fi
  # Shrinking is legal ONLY for a redaction, and a redaction has to say so.
  B_LINES="$(git show "FETCH_HEAD:$LEDGER" 2>/dev/null | wc -l)"
  A_LINES="$(wc -l < "$LEDGER")"
  if [[ "$A_LINES" -lt "$B_LINES" ]]; then
    if grep -q '^## Redaction log' "$LEDGER"; then
      say "note     the file is shorter than the remote's, and the redaction log is present"
    else
      bad "the file is SHORTER than the remote's ($A_LINES < $B_LINES) and has no redaction log"
      say "         Shrinking is allowed for one reason: taking a register value out."
      say "         Say so under a '## Redaction log' heading, or you are losing evidence."
    fi
  fi
else
  say "note     origin/$BRANCH not readable — first push, or no network"
fi

# ------------------------------------------------- 2. no register value, anywhere
REG="$HOME/.config/grimsverk/identity.json"
declare -a NEEDLES=()
if [[ -f "$REG" ]]; then
  while IFS= read -r v; do
    [[ -n "$v" && "${#v}" -ge 4 ]] && NEEDLES+=("$v")
  done < <(sed -nE 's/.*"[a-z_]+"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' "$REG")
  say "note     ${#NEEDLES[@]} value(s) read from the register"
else
  say "note     no register on this machine — generic shapes only (the web lane's case)"
fi

TRACKED="$(git ls-files test-kit 2>/dev/null)"
[[ -n "$TRACKED" ]] || TRACKED="$LEDGER"

for needle in ${NEEDLES[@]+"${NEEDLES[@]}"}; do
  hits="$(grep -n -F -- "$needle" $TRACKED 2>/dev/null | head -3)"
  if [[ -n "$hits" ]]; then
    bad "a register value appears in a tracked file:"
    printf '           %s\n' "$hits"
  fi
done

# Always, register or not: the shapes a leak takes.
while IFS='|' read -r label pattern; do
  hits="$(grep -nE -- "$pattern" $TRACKED 2>/dev/null | grep -v '<home>' | head -3)"
  if [[ -n "$hits" ]]; then
    bad "$label:"
    printf '           %s\n' "$hits"
  fi
done <<'PATTERNS'
an absolute home directory|/(home|Users)/[A-Za-z0-9_.-]+
an SSH host alias|git@github\.com-[A-Za-z0-9_.-]+
PATTERNS

echo
if [[ "$fail" -eq 1 ]]; then
  echo "check-ledger: REFUSED. Fix the items above before pushing." >&2
  echo "A register value found in anything pushed is itself a finding (rule 13)." >&2
  exit 1
fi
echo "check-ledger: clean — safe to push."
