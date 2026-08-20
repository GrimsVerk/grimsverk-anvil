---
slug: anvil-convert-batch   # MUST appear in every branch name working this plan
status: draft               # draft | in-flight | merged
created: 2026-08-20
design: Later — milestone `convert-batch` (docs/DESIGN.md §12)
covers: [R6, R1003, R1004]
---

# `anvil` batch mode — Plan

## Summary

**What this builds.** Milestone `convert-batch`: `anvil --batch` reads conversion
requests from standard input and writes exactly one line per request. It
implements **OD-7 / R1003** (the batch line format, resolving BL-8) and **OD-8 /
R1004** (undecodable input, resolving BL-9), and delivers the design's **R6**,
with `acceptance/S5.sh` as its evidence. It is third in the build order: it
extends the MVP plan's `cli.py` and `convert.py`, and touches no unit table.

**Decisions that are expensive to reverse.**

- **One shared request path.** `convert_request(...)` does parse → convert →
  format and raises `ConversionError` carrying the reason; single-shot `main` is
  refactored onto it. That makes R1003's "byte-identical to single-shot"
  structural rather than two code paths agreeing by hand.
- **No fourth module.** Batch lives in `cli.py`, as the MVP plan said it would.
- **The malformed-line reason is `malformed line: '<the line>'`** — R1003 leaves
  the wording here and requires it to name the offending input. A wrong field
  count on input line 3 prints `anvil: line 3: malformed line: '5 km'`.
- **This plan edits `acceptance/S3.sh`, one row.** S3 asserts that
  `anvil --batch` prints usage and exits 2; that expires the moment R6 lands, by
  R1001's own terms. The row becomes `anvil --batch extra` — still R5, still 2.
- **The usage text gains a second line**, `       anvil --batch`. The MVP left
  the flag out because it did not exist yet; usage that hides half the interface
  is the silent guess V2 rejects.
- **Output is written and flushed line by line**, so a batch answers each request
  as it is typed rather than at end of input.
- **Standard input is decoded with `errors="replace"`** — **OD-8 / R1004**: a bad
  byte becomes U+FFFD, its line refuses under an existing reason, the rest runs.

**What it costs you.** One new required check, `acceptance/S5.sh`, on every pull
request from here on; one user-visible change outside this milestone, the
two-line usage text. No dependency (V5 holds), no new module, no new exit code —
0, 1 and 2 keep the meanings the MVP gave them.

**Deliberately not done.** A file argument to `--batch`, a `--help` flag, unit
aliases (BL-1), absolute zero (BL-2), pretty output (BL-3, halted at OD-2),
currency (BL-4, rejected at OD-3).

**Open questions.** None. The one this plan carried — **BL-9** — is now ruled by
**OD-8 / R1004**, which confirms the default: no code direction changes, and
slice 1 gains the tests that prove it.

## Uncertainties

- **Q:** What happens when standard input carries bytes that are not valid
  UTF-8? R1003 fixes the line format but assumes every line decodes, and
  Python's text-mode `sys.stdin` raises `UnicodeDecodeError` on the first bad
  byte — which ends the batch with a traceback, no output line for that request,
  and no exit code of the tool's own choosing. That collides with R6's "a bad
  line … does not stop the remaining lines". — **risk:** LOW — every candidate
  answer is one line in `main`; it moves no slice boundary, changes no
  Signatures block, adds no shape to R1003's output grammar, and alters no
  expected byte in `acceptance/S5.sh`. — **proposed:** read standard input with
  `errors="replace"`, so undecodable bytes become U+FFFD and the affected line
  refuses through the ordinary R4 path — `unknown unit`, `not a number` or
  `malformed line`, whichever fits — while the remaining lines still run.
  **Ruling:** **OD-8 / R1004** (evidence **BL-9**) — decode with
  `errors="replace"`, exactly as proposed. The default this plan proceeded on is
  now a landed requirement, so slice 1's code direction stands unchanged and no
  reason text, exit code or output shape is added; what the ruling adds is the
  measurement, the `main`-driven tests in slice 1, because the decode happens in
  `main` and a test driving `run_batch` cannot observe it.

This plan raises no further uncertainty: OD-8 answers the only one it had, and
nothing in this amendment reaches past what that decision names.

### Derived, not guessed

These looked open and are not. The design layer answers each one, and the answer
is recorded here with what gave it:

- The request-line grammar, the error-line shape, the stream, blank-line
  skipping, the 1-based numbering that counts blanks, and the exit codes —
  **OD-7 / R1003**, in terms.
- The field order inside a request line — **R1001**, the same order as the
  single-shot positionals.
- How `--batch` is invoked, and that `anvil --batch extra` is a usage error with
  exit 2 — **R1001** and **R1003**.
- Every result line's text — **OD-1 / R1000**, `format(value, ".12g")`.
- Refusal of non-finite values and overflowing results inside a batch —
  **OD-5 / R1002**.
- That standard input is decoded with `errors="replace"`, that an affected line
  refuses like any other bad line, and that the batch never dies on a bad byte —
  **OD-8 / R1004**, in terms.
- Which existing reason a replaced line refuses under — **R1004** ("an existing
  reason") together with the MVP's message table: a field holding U+FFFD parses
  as no float and names no unit, so it lands on `not a number` or
  `unknown unit`, whichever field carried the byte.
- The reason text for each refusal — the MVP plan's message table, which R4
  delegated to it; R1003 requires the batch reason to be that same text.
- The malformed-line reason's wording — delegated by **R1003** ("stays with the
  plan, as R4 delegates wording") with one constraint, that it name the
  offending input, which `malformed line: '<the line>'` does.
- The usage text — delegated by **R5** and **R1001**, which require usage and
  fix its stream and exit code but not its words; the MVP chose the first line
  and gave the condition under which the second appears.
- That `acceptance/S3.sh` must change — **R1001** says `--batch` takes the
  usage-error path *until the `convert-batch` milestone lands R6*. This plan
  lands R6, so the assertion expires here. Keeping S3 true is not extending
  another plan's criterion; leaving it false would be breaking one.
- Module layout, names and signatures — delegated by **§7** and by the Planning
  rule, which makes the Signatures block the plan's job.

## The slices

Slices 1 and 2 both touch `src/grimsverk_anvil/cli.py`; slice 3 touches no file
in `src/`. **Assemble in order — 1, then 2 and 3 in parallel.**
`docs/architecture.md` is appended to by every slice, as `AGENTS.md` requires;
assembly reconciles it.

**The batch contract is fixed here, and both the coder and the test author work
from it.** `<n>` is the 1-based input line number, counting blank lines. Every
line below goes to **standard output**, in input order.

| Input line | Output line |
| --- | --- |
| `0.1 km m` | `100` |
| `1 mi km` | `1.609344` |
| `5 xyz m` | `anvil: line <n>: unknown unit: 'xyz'` |
| `5 kg m` | `anvil: line <n>: cannot convert 'kg' (mass) to 'm' (length)` |
| `abc km m` | `anvil: line <n>: not a number: 'abc'` |
| `inf km m` | `anvil: line <n>: not a number: 'inf'` |
| `1e308 km mm` | `anvil: line <n>: result is out of range: '1e308' km to mm` |
| `5 km` | `anvil: line <n>: malformed line: '5 km'` |
| `5 km mi extra` | `anvil: line <n>: malformed line: '5 km mi extra'` |
| `` (blank or whitespace only) | *no output line; `<n>` still advances* |
| `\xff km m` (a byte that is not valid UTF-8) | `anvil: line <n>: not a number: '<U+FFFD>'` |

Every reason except the two `malformed line` rows is the MVP's, character for
character — that is R1003's requirement, not a nicety. The quoted line in a
malformed reason is the input line with leading and trailing whitespace stripped
and no trailing newline; internal spacing is left as the user typed it.

The last row is **R1004** and adds no reason of its own: the bad byte is already
U+FFFD by the time the line is parsed, and U+FFFD parses as no float, so the line
lands on the `not a number` row above, with the replaced text echoed as the
offending input. A bad byte inside the from-unit or to-unit field lands on
`unknown unit` the same way.

**Exit codes.** 0 when no request failed — an empty standard input is a
successful batch of zero requests. 1 when any request failed. 2 for a wrong
argument shape, `anvil --batch extra` included, whose usage text goes to standard
error before any reading starts. Per-request output never goes to standard
error.

**Expected result strings are the MVP's.** Every conversion used in this plan's
tables already appears in `acceptance/S1.sh`'s vetted table, so this plan adds no
hand-derived arithmetic. If a sample and `format(value, ".12g")` ever disagree,
the format call is right and the disagreement is a finding for assembly.

## Slice 1 — `anvil --batch` converts a stream

- **Delivers:** `printf '0.1 km m\n1 mi km\n' | anvil --batch` prints `100` and
  `1.609344` and exits 0. A blank line produces no output line. Empty input
  produces no output and exits 0. A request the converter refuses prints
  `anvil: line <n>: <reason>` on standard output and makes the exit 1. Single-shot
  conversions still print exactly what they printed before. Bytes on standard
  input that are not valid UTF-8 never end the batch: the affected line refuses
  with an ordinary reason and every later line still converts (R1004).
- **Files:** `src/grimsverk_anvil/cli.py`, `tests/test_batch_stream.py`, `docs/architecture.md`
- **Estimate:** ~215 lines (was ~190; the three `main`-driven decode tests below
  are what OD-8 added — the decode argument itself was always in this slice)

**Scope of this slice.** Three functions in `cli.py`, plus the `--batch` branch
in `main`, plus the refactor that makes single-shot and batch share one path.

`convert_request` is that shared path: it parses the value with `float()`,
refuses a non-finite value and a non-finite result (R1002), converts through
`convert`, and returns `format_result(...)`. Every refusal raises
`ConversionError` whose `str()` is the reason text in the table above.
Single-shot `main` calls it and prints `anvil: {reason}` on standard error with
exit 1 — **the MVP's behaviour, unchanged, now in one place**. If the MVP left
this logic inline in `main`, this slice extracts it without changing one byte of
one message: `acceptance/S1.sh` and `acceptance/S3.sh` must stay green with no
edit in this slice. If either goes red, the extraction changed behaviour and that
is a finding for assembly, not something to fix by editing the script.

`parse_batch_line` returns `None` for a blank or whitespace-only line, returns
the three fields for a three-field line, and raises `ConversionError` with the
malformed reason for any other field count. Splitting on runs of whitespace is
`str.split()`, which also strips a trailing `\r` from CRLF input.

`run_batch` iterates the input with `enumerate(..., start=1)`, writes each output
line followed by `"\n"` and flushes, and returns 1 if any request failed and 0
otherwise.

`main` decodes standard input itself instead of using the decoder `sys.stdin`
already carries: it wraps `sys.stdin.buffer` in
`io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")`, passes
that to `run_batch` with `sys.stdout`, and holds the wrapper for the life of the
call. That one argument is **R1004**: a byte that is not valid UTF-8
becomes U+FFFD instead of raising `UnicodeDecodeError`, so the line survives as a
line and refuses through an existing reason while the rest of the batch runs.
Going through `.buffer` rather than `sys.stdin.reconfigure(errors="replace")` is
what makes the requirement testable — the tests below replace the binary stream,
which a reconfigured `sys.stdin` gives no way to do.

`tests/test_batch_stream.py` drives `run_batch` with `io.StringIO`, offline and
deterministic: the two-request happy path, a batch whose every line converts,
blank lines in the middle and at the end, whitespace-only lines, empty input,
input whose last line has no trailing newline, and a mixed batch returning 1. One
test uses a recording stream to assert one write per request in input order,
which is the streaming property the flush exists for.

Three further tests in the same file drive `main(["--batch"])` rather than
`run_batch`, with `sys.stdin` replaced by a stand-in whose `.buffer` is an
`io.BytesIO`. They have to go through `main`, because the decode happens there
and a `StringIO` cannot observe it — OD-8's measurement paragraph says so in
terms. Each asserts standard output exact-match, the exit code, and that standard
error is empty:

| Bytes on standard input | Standard output | Exit |
| --- | --- | --- |
| `b"\xff km m\n1 mi km\n"` | `anvil: line 1: not a number: '<U+FFFD>'` then `1.609344` | 1 |
| `b"1 k\xffm m\n5000 m km\n"` | `anvil: line 1: unknown unit: 'k<U+FFFD>m'` then `5` | 1 |
| `b"0.1 km m\n1 mi km\n"` | `100` then `1.609344` | 0 |

The first two are R1004's own case: the later line still converts, which is R6's
"a bad line does not stop the remaining lines" proven against a bad *byte*. The
third proves the wrapper leaves ordinary input alone. The expected reason texts
come from the contract table above, not from a new message; the test author reads
the replaced field as U+FFFD, exactly as the tool will print it.

### Signatures

```python
def convert_request(value_text: str, from_unit: str, to_unit: str) -> str: ...
def parse_batch_line(line: str) -> tuple[str, str, str] | None: ...
def run_batch(lines: Iterable[str], out: TextIO) -> int: ...
```

All three live in `cli.py`, beside `main` and `usage`. `convert`,
`format_result`, `ConversionError`, `lookup` and `UNITS` keep the signatures the
MVP plan declared; only `main`'s body changes.

## Slice 2 — the stream stays aligned, and the interface stops lying

- **Delivers:** every refusal in the contract table proven through a batch, with
  the line number counting skipped blanks; `anvil --batch extra` printing usage
  on standard error with exit 2; usage naming `--batch`; and
  `acceptance/S3.sh` telling the truth again.
- **Files:** `src/grimsverk_anvil/cli.py`, `acceptance/S3.sh`, `tests/test_batch_errors.py`, `docs/architecture.md`
- **Estimate:** ~150 lines

Code in this slice: the argument-shape branch that accepts `--batch` **only**
with no positionals, and the second usage line. The usage text becomes exactly:

    usage: anvil <value> <from-unit> <to-unit>
           anvil --batch

The first line is byte-identical to the MVP's, so an S3 assertion on that line
still holds.

`acceptance/S3.sh` changes in exactly one row: the invocation `anvil --batch`,
which asserted usage and exit 2, becomes `anvil --batch extra`. Nothing else in
that script moves — not a row, not an expected string, not the order. If the
script asserts the usage text exact-match rather than by its first line, extend
that assertion to the two-line text and say so in the commit message.

`tests/test_batch_errors.py` pins, through `run_batch` and through `main`:

- each reason row of the contract table, at a known line number;
- the numbering guarantee — a batch whose second line is blank and whose third
  line fails reports `line 3`, and the blank produces no output line;
- that a failing batch still processes every later line (R6);
- that per-request output goes to standard output and **standard error stays
  empty** for a mixed batch — the property OD-7 chose against the Unix default,
  so it is the one most worth pinning;
- exit 1 for any failure, exit 0 for an all-good batch and for empty input, and
  exit 2 with usage on standard error for `anvil --batch extra`.

### Signatures

No new signatures. `usage() -> str` keeps the MVP's signature and returns the
two-line text without a trailing newline.

## Slice 3 — S5 as executable evidence, and the README documents batch mode

- **Delivers:** `acceptance/S5.sh`, a required check on every pull request,
  proving R6 and R1003 against the installed command — and a README that
  documents batch mode.
- **Files:** `acceptance/S5.sh`, `tests/test_batch_acceptance.py`, `README.md`, `docs/architecture.md`
- **Estimate:** ~200 lines

`acceptance/S5.sh` is OD-7's measurement paragraph, item by item. It runs four
batches through the installed `anvil` command, comparing standard output
**exact-match**, which R1000 and R1003 together make deterministic.

**Batch A — §13 S5 itself: five lines, one invalid.**

| Input | Expected standard output |
| --- | --- |
| `0.1 km m` | `100` |
| `1 mi km` | `1.609344` |
| `5 xyz m` | `anvil: line 3: unknown unit: 'xyz'` |
| `2 lb oz` | `32` |
| `500 g kg` | `0.5` |

Four correct result lines, one error line naming the bad input, **in its stream
position** — the whole five-line output is compared as one block, not searched
for the error. Exit **1**. Standard error must be empty.

**Batch B — the blank line and the malformed line.**

| Input | Expected standard output |
| --- | --- |
| `1 ft in` | `12` |
| *(blank line)* | *(nothing)* |
| `5 km` | `anvil: line 3: malformed line: '5 km'` |
| `16 oz lb` | `1` |

Three output lines from four input lines, and the error says `line 3`, not
`line 2`. That single row is OD-7's items (b) and (c) at once: the skip and the
numbering are the same assertion.

**Batch C — all good.** `5000 m km` and `2500 mg g` print `5` and `2.5`, exit
**0**.

**Batch D — empty input.** No output, exit **0**.

**Parity.** `anvil 1 mi km` is run single-shot and its standard output compared
byte-for-byte with batch A's second line — OD-7's item (e), and the reason
`convert_request` is one function.

The script prints every batch, what it fed in, and what it observed — standard
output is the evidence cell — and follows `acceptance/README.md`:
`set -euo pipefail`, exit 0 is pass, offline, no mocks, fail on the first
mismatch naming both strings.

`tests/test_batch_acceptance.py` drives `main(["--batch"])` with the same four
batches through patched standard input and output, so the batches are covered by
the offline suite as well as by the acceptance check.

`README.md` gains batch mode to its usage section: the invocation, what a
request line looks like, what an error line looks like, that blank lines are
skipped, and that the exit code is 1 if any line failed.

### Signatures

No new signatures. This slice exercises `main` and `run_batch` as slice 1
declared them.

## Out of scope

- **Anything R1003 did not decide about batch:** a file argument, a header line,
  a delimiter option, comment lines, per-line timing, parallelism.
- **A dedicated "not valid UTF-8" reason**, and any byte-level reading of
  standard input beyond the one `errors="replace"` wrapper — OD-8 weighed that as
  its alternative (3) and rejected it, so building it here would re-decide a
  landed decision.
- **`acceptance/S1.sh` and `acceptance/S2.sh`** — other plans' criteria. This
  plan must leave every expected string in both byte-identical; slice 1's
  refactor is judged by that.
- **`acceptance/S3.sh` beyond the one row** named in slice 2. Adding batch cases
  to S3 would be extending another plan's criterion; repairing the assertion
  that R6 invalidates is not.
- **BL-1 (aliases), BL-2 (absolute zero), BL-3 (`rich`, halted at OD-2),
  BL-4 (currency, rejected at OD-3).** None is planned here, and OD-2 forbids
  even a stdlib approximation of BL-3.
- **`docs/acceptance.md`** — filled by the acceptance pass, not by this plan.
- **`docs/escapes.md`** — this plan closes no escape, and `AGENTS.md` forbids a
  change carrying its own ledger entry in any case.
