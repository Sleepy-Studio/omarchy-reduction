# omarchy-reduction

For Hermes and any agent working in this directory.

**Read `knowledge-base/INDEX.md` and `knowledge-base/SCHEMA.md` before
changing anything.** Half this repository is an argument for leaving the
system alone, and that half is load-bearing.

## What this is

A public, amendable knowledge base assessing **Omarchy as a system** — its
command surface, its shell, its install footprint, its runtime cost, and its
extension mechanisms.

Every number in every record is produced by `tools/measure.py` from `/usr/bin`
and `/usr/share/omarchy`, and re-checked by `run-tests.sh`. Nothing is typed
from memory.

**This is not a fork and not a rewrite, and it implements nothing.** Records
describe, argue, and measure. Nothing here changes the installed system, and no
PR may. If you want to act on a record, that is a patch to Omarchy — upstream
or local — and it belongs in a different repository.

## The split, and why it is strict

```
knowledge-base/   written.     the records, the schema, the index
baseline/         generated.   measurements.json, machine-read, never hand-edited
tools/            the measurer and the record validator
```

`baseline/measurements.json` is **generated**. If a number is wrong, fix
`tools/measure.py` and re-measure — never patch the JSON. Committing a
re-measured baseline is only worth it when something *structural* moved and you
have re-checked every record that quotes it; a diff of volatile fields alone
carries no information.

`run-tests.sh` step 2 validates every record against `SCHEMA.md` and step 3
re-checks every headline number quoted in prose against the baseline. A record
that drifts is a broken build, not something to notice by reading.

## Verifying

```bash
bash run-tests.sh           # everything, six gates
bash tools/measure.sh       # just the measured table
python3 tools/validate-kb.py   # just the records
```

Headless and safe at any time. Reads `/usr/bin` and `/usr/share/omarchy` only.
Runs no state-changing command, sends no input, maps no window, captures no
screen, and never restarts or rescans the shell.

## Never put anything on the user's screen to test it

Same boundary as the rest of `~/Projects` — see the root `AGENTS.md`. This
project never loads QML and cannot: it reads source and measures a running
process. `run-tests.sh` runs the shared lint as a gate:

```bash
node ~/Projects/lib/lint-no-visible-surfaces.js
```

## Step 0, and the two rules under it

`run-tests.sh` **executes** `tools/measure.sh`. Any check on that file placed
after the run is already too late — a state-changing command planted in the
measurer has fired by the time you grep for it.

This is not hypothetical. While building the sibling project `homelpy`, a
self-test appended a real `omarchy theme set nord` to that repo's generator.
The suite ran the script, the theme changed, and only *then* did the gate
report it.

Two rules generalise past this repo:

- **Never test a gate by mutating the thing the gate protects.** Verify against
  a copy, with a `--dry-run`, or by planting a command in a file nothing
  executes.
- **A gate that reports after the fact is not a gate.** It is a log line.

Step 0 here is a static grep, and if it trips the suite refuses to execute the
measurer at all.

**Verify it on a copy, never on the live tooling:**

```bash
T=$(mktemp -d); cp -r . "$T"/
printf '\nomarchy theme set nord\n' >> "$T"/tools/measure.py
(cd "$T" && bash run-tests.sh)   # must FAIL at step 0
rm -rf "$T"
```

The record validator deserves the same treatment. A validator that never fails
is worthless, and the way to know it fails is to feed it a broken record **on a
copy**:

```bash
T=$(mktemp -d); cp -r . "$T"/
cat > "$T"/knowledge-base/findings/KB-999-broken.md <<'EOF'
---
id: KB-001-capability-facades
title: Deliberately broken
type: reduction
status: nonsense
strength: strong
measuredOn: 30-09-2026
amendments: 7
---

## Problem
Only two sections, and a duplicate id.
EOF
(cd "$T" && python3 tools/validate-kb.py)   # must FAIL, naming the problems
rm -rf "$T"
```

## Working on the records

- Amend an existing record; do not create a rival one. If you disagree with a
  proposal, it goes in that record's `## Cons`, with a history line.
- **`defence` records are first-class.** A knowledge base that only lists
  things to change is not a knowledge base.
- `status: rejected` with a stated reason is a good outcome — it stops the
  next person re-proposing the same thing.
- Never edit earlier `## Amendment history` lines. Append.
- Never state an unmeasured number as fact. Cite
  `baseline/measurements.json` or mark it `strength: speculative`.
- Add every new record to `knowledge-base/INDEX.md`; `run-tests.sh` fails on a
  record the index does not link.

## Honesty rules specific to this repo

**Appearance cannot be verified here.** By the root rule, an agent cannot check
how something looks on a screen. Where a record says a change would be
"visually identical", that is a claim for a human, and it must be marked
unverified in the record. KB-020 is the clearest case: the measurement is
solid, the harmlessness is asserted.

**A record may recommend not doing something.** The defence records are the
ones that keep this repository from being a wish-list. When you conclude the
right answer is "leave it", write that down with the same rigour as a
proposal — including the one defensible narrow case and the reason not to take
it.

**The measurements were taken on one machine.** Another reader's numbers will
differ. That is expected, not a broken baseline, and `CONTRIBUTING.md`
explains which differences are meaningful (structural) and which are noise
(volatile).