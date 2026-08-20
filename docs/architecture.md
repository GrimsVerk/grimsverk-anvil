# grimsverk-anvil — Architecture

<!-- The living description of what exists RIGHT NOW. Updated at the end of every
slice (AGENTS.md, "Architecture doc"), so it describes the system as built, never
as planned. `docs/DESIGN.md` is the intent and doesn't change; this changes.

Keep it at the level of LOGIC, NOT CODE. Components and what each is responsible
for, what data moves between them, what happens on the main paths. No signatures,
no line-by-line description, nothing that a rename would invalidate — if a
refactor that changes no behaviour would force an edit here, it's too low-level.

It has two readers and they keep each other honest: the owner, who does not read
the code and needs somewhere to understand the system; and the next agent, which
starts with no context beyond this repository and reads this first to get its
bearings. Written for the human, it stays truthful; written at all, it saves the
agent from rediscovering the system by grepping.

Delete these comments or leave them; they don't render. -->

## Components

<!-- One entry per component: its name, and the single thing it is responsible
for. If a component needs "and" to describe its responsibility, say so plainly —
that's worth seeing. -->

| Component | Responsible for |
| --- | --- |
| Unit table | Holding every known unit symbol with its category (length or mass) and its factor to that category's base unit — metre, gram. Symbols match exactly. |
| Unit lookup | Answering "is this symbol known?" with the unit or with nothing. |
| Converter | Turning a number plus two unit symbols into a number, through the category's base unit. It refuses an unknown symbol and a cross-category pair. |
| Result formatter | Turning a converted number into the one printed form the precision rule fixes. |
| Request path | The single shared route for one request: read the value, refuse a value or a result that is not finite, convert, format. Every refusal carries the user-facing reason with it. |
| Batch line parser | Turning one input line into three fields, into nothing (a blank line), or into a refusal that quotes the offending line. |
| Batch runner | Walking the input lines in order, numbering them from 1, writing one output line per request, and reporting whether any request failed. |
| Command entry point | Choosing between batch mode, single-shot conversion and the usage error, and owning the exit code. |

The components sit in three modules, as the plans declare. The unit table and
the unit lookup are one module. The converter, the result formatter and the
refusal type are the second. The command entry point, the request path, the
batch line parser and the batch runner are the third, and it reads from the
other two.

## Data flow

<!-- What moves between the components, in what direction, and in what form.
Prose or a simple list is fine — `A --(what)--> B`. A diagram is welcome but
never required; an accurate list beats a stale picture. -->

- Command entry point --(three text fields)--> Request path
- Batch runner --(one input line)--> Batch line parser --(three text fields)--> Request path
- Request path --(number, two symbols)--> Converter --(symbol)--> Unit lookup --> Unit table
- Converter --(number)--> Request path --(number)--> Result formatter --(one text line)-->
  Request path
- Request path --(refusal reason, raised)--> its caller, which decides where the reason is
  printed and what the exit code becomes

The refusal reason is written in one place and both modes use it. That is
deliberate: the batch reason must be the single-shot reason character for
character, so the two cannot drift apart.

## Main paths

<!-- Walk the two or three journeys that matter, start to finish, in plain
language: what triggers it, which components it touches in order, what the
observable result is. These are what someone reads to understand how the system
actually behaves, and they are the first thing to go stale — check them at the
end of each slice. -->

### Single-shot conversion — `anvil 0.1 km m`

1. The command entry point sees exactly three arguments. It calls the request path.
2. The request path reads the value, converts it, and formats the result.
3. The result goes to standard output. The exit code is 0.
4. If the request path refuses, the reason goes to standard error as
   `anvil: <reason>` and the exit code is 1.

### Batch conversion — `anvil --batch`

1. The command entry point sees `--batch` alone. It decodes standard input itself,
   as UTF-8, and replaces any byte it cannot decode with the replacement character.
   This is why a bad byte cannot end a batch: the line stays a line.
2. The batch runner walks the decoded lines and numbers them from 1. A blank or
   whitespace-only line gives no output line, but it still uses up a number.
3. Each other line goes to the batch line parser, then to the request path.
4. The answer — a result, or `anvil: line <n>: <reason>` — goes to standard output
   and is flushed at once, so each request is answered as it arrives. Per-request
   output never goes to standard error.
5. The exit code is 1 if any request failed, and 0 if none did. Empty input is a
   successful batch of zero requests.

### Wrong argument shape — `anvil`, `anvil --help`, `anvil --batch extra`

1. The command entry point matches neither shape.
2. The usage text goes to standard error, before any input is read. The exit code
   is 2.

## State and storage

<!-- Optional. What persists, where it lives, and what owns it. Skip if the
system holds nothing. -->

## Known rough edges

<!-- Optional but valuable. Things that work but are awkward, deliberate
shortcuts, and where the next change in this area is likely to hurt. This is the
section that stops a future agent confidently "fixing" something load-bearing,
and it's where the reviewer's "easy to change next time" findings should land
when they're accepted rather than acted on. -->

- **The convert MVP milestone has not been built yet**, although its three
  modules now exist. The batch plan was built first, so `units.py`, `convert.py`
  and `cli.py` were created here, holding only what batch mode needs. The MVP
  slices add to them rather than creating them.
- **The usage text names only the single-shot form**, although batch mode now
  works. Slice 2 of the batch plan adds the second line.
- **`pyproject.toml` has no `[project.scripts]` entry yet**, so there is no
  installed `anvil` command. The entry point is called directly for now.
