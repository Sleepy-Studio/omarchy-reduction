---
id: KB-005-large-qml-files
title: Breaking up the 2,000-line QML files would make them worse
type: defence
status: accepted
strength: strong
surface: shell
confidence: medium
measuredOn: 2026-09-30
amendments: 0
---

## Problem

The largest files in the shell:

| file | lines |
|---|---|
| `plugins/bar/Bar.qml` | 2,076 |
| `shell/shell.qml` | 1,744 |
| `plugins/panels/network/Panel.qml` | 1,970 |
| `plugins/menu/Menu.qml` | 1,427 |

Large QML files read as a code smell. "Break up the 2,000-line file" is
standard advice, and applying it here would be a mistake.

QML is **declarative**. A `Rectangle` with seven properties is not seven lines
of logic — it is a description, and reading it top to bottom in one place is how
you understand it. Splitting along line boundaries produces files that each
need three others open to be read at all, and it moves the difficulty from
"scroll more" to "hold more context in your head". That is a regression, not a
refactor.

This is the record most likely to be disagreed with, which is why its
`confidence` is `medium` and not `high`.

## Proposal

**Leave them.** Specifically:

- Do not split `Bar.qml` or `shell.qml` by arbitrary boundaries.
- Do not extract "helpers" from them for tidiness. The domain content — the
  tray, the clock, the indicators, the panel routing — belongs where it is.

**The one defensible narrow case:** `Bar.qml` declares its layout as six
`Component`s — left/center/right × horizontal/vertical — in the region around
lines 1271–1591. Six variants of one structure is a table, and a table is
genuinely more honest than six near-copies. That is the only part of this
record that proposes anything, and it is small.

And even there, the cost is real: `Component`-per-variant is idiomatic QML and
readable as written. A table-driven version is denser, and a layout bug in a
denser file is harder to diagnose — especially by anyone debugging without a
visual debugger.

## Pros

- **Declarative code rewards locality.** The whole value of a layout file is
  that you can read it and see the structure. Splitting removes that.
- **The current arrangement is what makes `Bar.qml` navigable**: the six layout
  variants are adjacent and comparable, which is why the duplication is
  visible as duplication rather than hidden in two places.
- **QML tooling is weak.** No good visual diff, no refactor support, poor
  cross-file navigation. Splitting a large declarative file without tooling
  support is a bet against the reader.
- The files are large but not growing pathologically: `shell.qml` at 1,744
  lines coordinates ~35,000, which is a plausible ratio for a root component.

## Cons

- **"Large declarative file" is a rationalisation, and it has a limit.** Some
  point, a file stops being readable in one pass. This record does not
  establish where that point is, and 2,076 lines is enough that somebody
  reasonably thinks it has been passed.
- **A single file is a single point of merge conflict.** A 2,076-line `Bar.qml`
  means every bar change conflicts with every other bar change. Splitting would
  genuinely reduce that, and it is the strongest argument against this record.
- **Testability.** Nothing in a monolithic QML file can be instantiated alone.
  Splitting would allow a layout component to be tested in isolation — though
  by this project's own rule that test cannot check appearance anyway, which
  substantially weakens the argument.
- The narrow case (`Component` table) is a concession, and a concession that
  concedes something is a precedent for the next proposal.

## Risk

**Not a risk so much as a cost of being wrong.**

If the file *is* past the readability limit, the symptom is that changes to it
become slow and error-prone — a soft, cumulative cost that is easy to
rationalise away indefinitely and hard to notice from inside the codebase.

The mitigation is not "split it", it is evidence: if someone finds a concrete
change that is hard *because* of the file's size, that is the evidence this
record is missing, and the right response is to narrow the change, not to
restructure 2,076 lines.

## Evidence

```bash
# the sizes
find /usr/share/omarchy/shell -name '*.qml' -exec wc -l {} + | sort -rn | head -12

# the six layout variants — the one narrow case, in the source
sed -n '1271,1300p' /usr/share/omarchy/shell/plugins/bar/Bar.qml
grep -n "Component {" /usr/share/omarchy/shell/plugins/bar/Bar.qml | head -20

# that the variants are adjacent and comparable, which is the readability
# argument made concrete
sed -n '1541,1600p' /usr/share/omarchy/shell/plugins/bar/Bar.qml
```

To overturn this record: find a specific change to `Bar.qml` that is hard
because of its size, and write it down. That is the evidence that would move
`confidence` to `high` — in either direction.

## Amendment history

- 2026-09-30 — initial record.