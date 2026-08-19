---
title: grimsverk-anvil
status: approved         # draft | in-review | approved
created: 2026-08-19
related: []
---

# grimsverk-anvil — Design Doc

<!-- TEST NOTE (deliberate, owner-authored): this design is the fixed input of
a template test. Two gaps are left in it ON PURPOSE, so the planner has to file
uncertainties and the oracle has to rule: (a) the output precision/rounding is
never specified, and (b) the exact command-line syntax is never specified. Do
not "fix" this document to close them — the gaps are the test. -->

## 1. Summary

`anvil` is a small command-line tool that converts a number from one unit to
another: lengths, masses, and temperatures. You give it a value, the unit it is
in, and the unit you want; it prints the converted value. It runs offline, uses
only the Python standard library, and is deliberately tiny — it exists to give
the delivery pipeline something real to build.

## 2. Problem & motivation

Quick unit conversions usually mean a search engine or a phone. A local CLI
answers instantly, works offline, and is scriptable. The real motivation is one
level up: this project is the test anvil for the grimsverk-template pipeline —
small enough to finish overnight, real enough that every gate, role, and check
gets exercised honestly.

## 3. Goals and non-goals

**Goals**
- Convert between common units of length, mass, and temperature, correctly.
- Fail loudly and helpfully on bad input.
- Stay dependency-free and offline.

**Non-goals**
- Currency, time zones, or any unit that needs live data.
- A GUI, a web service, or configuration files.
- Locale-aware number formatting.

## 4. Users & core use cases

- As a terminal user, I want to convert 5 kilometres to miles so that I get the
  number without leaving the shell.
- As a script author, I want a non-zero exit code on bad input so that my
  script can tell success from failure.
- As a cook, I want 350 fahrenheit in celsius so that I can set the oven.

## 5. Requirements

**Functional**
- **R1** — Convert between length units: m, km, cm, mm, mi, ft, in — *Evidenced by:* S1
- **R2** — Convert between mass units: kg, g, mg, lb, oz — *Evidenced by:* S1
- **R3** — Convert between temperature units: C, F, K, including the offset
  math (not a pure factor) — *Evidenced by:* S2
- **R4** — On an unknown unit, a cross-category conversion (e.g. kg to m), or a
  value that is not a number: print an error message that names the offending
  input, and exit non-zero — *Evidenced by:* S3

**Non-functional**
- **R5** — Platform / targets: *(non-functional)* a Python CLI, installed as
  the console command `anvil` from package `grimsverk_anvil` — *Evidenced by:* S4
- **R6** — Dependencies: *(non-functional)* Python standard library only;
  fully offline and deterministic — *Evidenced by:* S4

## 6. Constraints & assumptions

- Python, src layout, as scaffolded by grimsverk-template.
- No third-party runtime dependencies (see docs/VISION.md, V5).
- Assumption: integer and decimal inputs both occur; scientific notation may be
  ignored.

## 7. Proposed approach (high level)

- A conversion table module: unit → category and factor (temperatures as
  functions, since they are affine, not linear).
- A converter: (value, from-unit, to-unit) → result, or a typed error.
- A thin CLI layer that parses arguments, calls the converter, prints, and maps
  errors to exit codes.

## 8. Key design decisions & alternatives

- Decision: conversions go through a canonical base unit per category (metre,
  gram, kelvin).
  Options considered: pairwise factor matrix; base-unit hub.
  Choice & rationale: base-unit hub — O(n) table instead of O(n²), and adding a
  unit is one line.
- Decision: temperature handled as functions, not factors.
  Options considered: pretend factors are enough; special-case functions.
  Choice & rationale: functions — Fahrenheit/Celsius have offsets, factors
  silently produce wrong answers.

## 9. Data model / key entities

A unit table: `{unit_symbol: (category, to_base, from_base)}`. Nothing is
stored; the tool has no state.

## 10. External dependencies & integrations

None. Standard library only (R6).

## 11. Risks & open questions

- How many decimals should output carry, and how is it rounded? Not decided
  here.
- The exact command-line syntax (positional `anvil 5 km mi` vs flags) is not
  decided here.

## 12. Milestones / phasing

**MVP**
- Scope: length and mass conversions (R1, R2) with error handling (R4).
- Acceptance criteria: S1 and S3 pass.

**Later**
- Temperature (R3): S2 passes.

## 13. Success criteria

- **S1** — *(covers R1, R2)* — A fixed table of at least 10 known length and
  mass conversions produces the expected values when run through the installed
  `anvil` command.
- **S2** — *(covers R3)* — 100 C converts to 212 F and to 373.15 K, and a
  C→F→K→C round trip returns to the start value; verified through the installed
  `anvil` command.
- **S3** — *(covers R4)* — Running `anvil` with an unknown unit, with a
  cross-category pair, and with a non-numeric value each exits non-zero and
  prints a message naming the offending input.
- **S4** — **(owner)** *(covers R5, R6)* — The owner runs one conversion on
  their own machine from a clean checkout with no network, and judges the tool
  present, instant, and dependency-free.
