# The index

Every finding is one file, amendable on its own, validated against
[`SCHEMA.md`](SCHEMA.md). Start here, then open one record.

The gate `run-tests.sh` runs: every record validates, is listed here, and any
headline number it quotes is the number `baseline/measurements.json` actually
holds.

## Worth doing, close to free

| record | what | value | risk |
|---|---|---|---|
| [KB-020](findings/KB-020-wallpaper-resolution.md) | ship wallpapers at display resolution | 97% of the install, decodes to 4.5 GB | low — but see the unverified appearance claim |
| [KB-021](findings/KB-021-prebuilt-command-index.md) | build the routing table once | ~45 ms → a few ms, on every command | low **if** the fallback exists |
| [KB-025](findings/KB-025-duplicate-command-bodies.md) | two nvim commands are byte-identical | one line, one file | very low |

## Worth doing carefully

| record | what | value | risk |
|---|---|---|---|
| [KB-022](findings/KB-022-argument-dispatch-collapse.md) | collapse argument-dispatch commands | ~34 files → 3 | **highest here** — silently breaks keybinds |
| [KB-023](findings/KB-023-shared-polling-primitive.md) | one `CachedPoll` under the panel models | ~300–400 lines, uniform failures | moderate, quiet — scope to 4 panels |
| [KB-024](findings/KB-024-migration-pruning.md) | stop shipping dead migrations | unbounded growth | high per-machine, low as policy |
| [KB-026](findings/KB-026-bash-helper-library.md) | shared bash helpers | ~400–600 lines, `usage()` × 33 | low; smallest value here, `speculative` |

## Do not touch

These look reducible. They are not. Each is a finding in its own right, and
arguing them is as valuable as proposing something.

| record | what | why it stays |
|---|---|---|
| [KB-001](findings/KB-001-capability-facades.md) | 6 capability facades | narrowing a wide door; simplifying it widens it |
| [KB-002](findings/KB-002-auth-isolation.md) | three auth mechanisms | three because one was not enough |
| [KB-003](findings/KB-003-single-process-shell.md) | one process, 35k lines QML | the obvious refactor is strictly worse |
| [KB-004](findings/KB-004-themed-templates.md) | one palette → 19 app configs | the best abstraction in the system |
| [KB-005](findings/KB-005-large-qml-files.md) | 2,076-line `Bar.qml` | large QML is not a defect; splitting makes it worse |

## The measurements

Facts with no recommendation attached — the substrate the other records argue
from. [KB-014](findings/KB-014-migrations-unbounded.md) is the one honest open
question.

| record | measures |
|---|---|
| [KB-010](findings/KB-010-command-surface-shape.md) | 445 commands: size distribution, hidden, families |
| [KB-011](findings/KB-011-dispatcher-cost.md) | the ~45 ms dispatcher, and why it exists |
| [KB-012](findings/KB-012-install-footprint-wallpapers.md) | 121.7 MB install, 97% themes, 4.5 GB decoded |
| [KB-013](findings/KB-013-panel-data-models.md) | 10 panel models, 2,137 lines, no shared layer |
| [KB-014](findings/KB-014-migrations-unbounded.md) | 106 migrations, never pruned — **open** |

## The one-line summary

The extensibility surface is **tiny** — 5 hook events, 6 capability facades —
and the implementation surface is **enormous**: 34,842 lines of bash across 445
commands, 34,914 lines of QML. That ratio is the whole story, and it cuts both
ways: it is why the system is easy to extend in the ways it was designed for,
and why it is hard to reason about in the ways it was not.

## Contributing

See [`../CONTRIBUTING.md`](../CONTRIBUTING.md). Amend a record rather than
creating a rival one. `status: rejected` with a stated reason is a good
outcome — it stops the next person re-proposing the same thing.