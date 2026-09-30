# Contributing

This is a knowledge base about Omarchy, not a fork of it. **Nothing in this
repository changes the behaviour of your installed system.** Every record is a
description, an argument, or a measurement.

The point is to make the assessment better in public: one record per idea,
each independently amendable, each with its counter-argument written down so
disagreement has somewhere to go.

## The loop

1. **Read the record** you want to change. Start with
   [`knowledge-base/INDEX.md`](knowledge-base/INDEX.md).
2. **Measure it yourself.** Every claim has an `## Evidence` section with
   commands that reproduce it on your machine. If the number differs from the
   record, the record is wrong — say so.
3. **Amend the record.** Not a new file. Bump `amendments`, add a line to
   `## Amendment history`, change the substance.
4. **Run the suite.** `bash run-tests.sh` — it validates every record against
   [`knowledge-base/SCHEMA.md`](knowledge-base/SCHEMA.md) and checks that the
   numbers in the prose still match `baseline/measurements.json`.
5. **Open a PR** explaining what changed and what you measured.

GitHub Discussions is for the questions that are not yet records —
"is this a problem anyone else has?", "what is the supported upgrade
window?". Answer one there and it can become a record.

## Adding a record

Copy any existing file in `knowledge-base/findings/`, change the `id` to
something new and unique (**never reuse an id** — the id is the anchor that
survives the record being rewritten), and fill in all seven sections.

```bash
cd knowledge-base/findings
cp KB-020-wallpaper-resolution.md KB-030-your-idea.md
$EDITOR KB-030-your-idea.md
bash run-tests.sh          # will fail until every field is filled in
```

The four types:

- `reduction` — something could be smaller or simpler
- `defence` — something looks reducible and should **not** be. Also a finding.
- `measurement` — a measured fact with no recommendation attached
- `open-question` — unresolved; needs investigation or upstream discussion

**A `defence` record is a real contribution.** If you think something is right
and should stay, that belongs here too. A knowledge base that only lists things
to change is not a knowledge base.

## Amending well

The `## Cons` section is the one that matters most. It is the case against the
proposal, written by someone who wants to keep things as they are. A record
whose cons are soft is not ready to be accepted, and that is enforced socially
rather than by a gate — the schema requires the section, not its quality.

House rules:

- **Cite a measurement or mark it speculative.** Never state a number as fact
  without a path to where it came from.
- **Disagreement goes in the record.** If you think a proposal is wrong, add it
  to that record's `## Cons` and note it in the history. Do not create a
  rival record.
- **`status: rejected` is a good outcome.** Writing down why a plausible
  reduction was rejected stops the next person re-proposing it. This is the
  highest-value amendment anyone can make.
- **Do not edit earlier history lines.** That is what makes the history worth
  reading.
- **Bump `amendments` only for substance.** Wording fixes do not count.

## Numbers and machines

The committed `baseline/measurements.json` was measured on **one machine**.
Other machines will differ. That is expected and is not a broken baseline.

If your numbers differ, that is a finding:

- **Structural** numbers (command count, QML lines, plugin count, migration
  count) should match if you are on a comparable version. If they do not, you
  are on a different Omarchy version and the record may need re-dating —
  check `omarchy version`.
- **Volatile** numbers (dispatcher milliseconds, RSS, process count) will
  differ and always will.

To re-measure on your machine:

```bash
bash tools/measure.sh            # human-readable
bash tools/measure.sh --json     # the full JSON
```

Do **not** commit a re-measured `baseline/measurements.json` just because
yours differs on volatile fields — it creates a diff with no information. Only
commit it when something structural moved and you have re-checked the records
that quote it.

## What is deliberately absent

- **No implementation.** Records describe; nothing here patches anything.
- **No appearance claims.** By the rule this project is built under, an agent
  cannot verify how something looks. Where a record says "no visible
  difference", that is a claim for a human to check, and it is marked as
  unverified in the record.
- **No secrets, no personal paths.** `baseline/` is generated from paths under
  `/usr` and `/etc`. If your machine contributes something identifying, do not
  commit it — check before opening the PR.

## Running the suite

```bash
bash run-tests.sh
```

Headless and safe at any time. Reads `/usr/bin` and `/usr/share/omarchy` only.
Runs no state-changing command, sends no input, maps no window, captures no
screen, and never restarts or rescans the shell.

Step 0 is a static grep that **refuses to execute the measurer** if it finds a
state-changing command in it. That is not paranoia: the suite runs the
measurer, so a check placed after the run would be too late. While building the
sibling project `homelpy`, a self-test appended a real `omarchy theme set nord`
to that repo's generator, the suite ran it, and the theme changed before the
gate could report it.

To check that step 0 still works — **on a copy, never on the live tooling**:

```bash
T=$(mktemp -d); cp -r . "$T"/
printf '\nomarchy theme set nord\n' >> "$T"/tools/measure.py
(cd "$T" && bash run-tests.sh)   # must FAIL at step 0
rm -rf "$T"
```

## Licence

The measurements are facts about a system and freely reusable. The prose is
CC BY-SA 4.0 so it can be quoted and adapted with credit. See
[`LICENSE`](LICENSE).