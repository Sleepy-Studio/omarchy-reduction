# omarchy-reduction

A public, amendable knowledge base assessing **Omarchy as a system**: what
could be smaller, what would be strictly better if it were, and — deliberately,
and in roughly equal measure — what should not be touched at all.

**Nothing here implements anything.** Every record describes, argues, or
measures. The installed system is never changed by this repository.

```bash
bash tools/measure.sh      # the measured table, from the live system
bash run-tests.sh          # proves the knowledge base still matches reality
```

Both are headless and safe at any time. Read-only: no state-changing command,
no input sent, no window mapped, no screen captured, the running shell never
touched.

## Read this first

**[`knowledge-base/INDEX.md`](knowledge-base/INDEX.md)** — every finding, one
row each, sorted by whether it is worth doing and whether it is safe.

Then pick one record. Each is self-contained: the measured problem, a specific
proposal, the case for, **the case against**, the risk, and how to verify it
yourself.

## The finding in one paragraph

The extensibility surface is **tiny** — 5 hook events, 6 capability facades —
and the implementation surface is **enormous**: 34,842 lines of bash across 445
commands, and 34,914 lines of QML in the shell. That ratio is the whole story.
Three reductions are clearly worth doing and are close to free: ship wallpapers
at display resolution (they are 97% of the install and decode to 4.5 GB),
prebuild the command index the dispatcher re-derives on every invocation
(~45 ms → a few ms), and stop shipping migrations that can no longer be needed
(106 of them, never deleted). Two more are worth doing carefully. One is
speculative. And the five **defence** records — the things that look reducible
and are not — are half the repository, because a knowledge base that only lists
things to change is not a knowledge base.

## Layout

```
omarchy-reduction/
  README.md                 this file
  PUBLISHING.md             the launch checklist — git remote, labels, placeholders
  CONTRIBUTING.md           how to measure, amend, add a record
  AGENTS.md                 for agents working in this repo
  LICENSE                   CC BY-SA 4.0 for the prose
  knowledge-base/
    SCHEMA.md               the record schema — read before amending
    INDEX.md                every finding, one row each
    findings/
      KB-001-capability-facades.md          defence
      KB-002-auth-isolation.md              defence
      KB-003-single-process-shell.md        defence
      KB-004-themed-templates.md            defence
      KB-005-large-qml-files.md             defence
      KB-010-command-surface-shape.md       measurement
      KB-011-dispatcher-cost.md             measurement
      KB-012-install-footprint-wallpapers.md measurement
      KB-013-panel-data-models.md           measurement
      KB-014-migrations-unbounded.md         open question
      KB-020-wallpaper-resolution.md        reduction
      KB-021-prebuilt-command-index.md      reduction
      KB-022-argument-dispatch-collapse.md  reduction
      KB-023-shared-polling-primitive.md    reduction
      KB-024-migration-pruning.md           reduction
      KB-025-duplicate-command-bodies.md    reduction
      KB-026-bash-helper-library.md         reduction
  baseline/
    measurements.json       generated — measured from the installed system
  tools/
    measure.sh / measure.py      the measurement
    validate-kb.py               every record against SCHEMA.md
  run-tests.sh               6 gates; step 0 refuses to run an unsafe measurer
```

## Why a knowledge base and not a report

A report is read once and goes stale silently. Every number here is generated,
and `run-tests.sh` fails if the prose no longer matches the measurements — so an
assessment that drifts is a broken build, not something you have to notice.

Each finding is a **separate record** so that one can be amended, disagreed
with, or rejected without touching the others. Every record carries its own
`## Cons` section, written as the case against its own proposal, because that
is where the argument actually lives.

And a rejected record is a good outcome: writing down *why* a plausible
reduction was rejected is the single most useful thing a reader can do.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md). The short version:

1. Read the record you want to change.
2. **Measure it yourself** — every record has an `## Evidence` section with
   commands that reproduce it. If your number differs, the record is wrong.
3. **Amend that record.** Bump `amendments`, add a history line, change the
   substance.
4. `bash run-tests.sh` — validates every record and checks the numbers.
5. Open a PR saying what you measured.

GitHub Discussions is for questions that are not yet records.

## Two things this repository will not do

**It will not claim to verify appearance.** By the rule this project is built
under, an agent cannot verify how something looks on a screen. Where a record
says a change would be "visually identical", that is a claim for a human to
check, and it is marked unverified in the record.

**It will not implement its own proposals.** These records describe. If you
want to act on one, that is a patch to Omarchy — upstream or local — and it
belongs in a different repository.

## Licence

Prose is [CC BY-SA 4.0](LICENSE) so it can be quoted and adapted with credit.
`baseline/measurements.json` is measured facts about an installed system and is
freely reusable.