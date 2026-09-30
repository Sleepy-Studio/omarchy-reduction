---
id: KB-026-bash-helper-library
title: One shared helper library, for the conventions duplicated 33 times
type: reduction
status: proposed
strength: speculative
surface: commands
confidence: medium
measuredOn: 2026-09-30
amendments: 0
---

## Problem

445 independent bash files, and no shared library — the files source nothing
from each other. The conventions that would be shared are re-implemented:

| function | files defining their own |
|---|---|
| `usage()` | 33 |
| `fail()` | 13 |
| `main()` | 7 |
| `cleanup()` | 7 |
| `confirm()` | 3 |
| `log()` | 3 |
| `show_help()` | 2 |

`usage()` being defined 33 times is the clearest signal: the argument-parsing
convention for omarchy commands is 33 separate interpretations of it, and
there is nothing that makes them agree.

The duplication is worth roughly 400–600 lines.

## Proposal

One `omarchy-lib.sh`, sourced by the commands that want it, holding only the
genuinely shared helpers: `usage`, `fail`, `confirm`, `log`. The long tail of
one-off helpers stays where it is.

**This is the smallest-value item in the knowledge base and it is marked
`speculative` deliberately.** The line-count saving is not the point — the
consistency is. Whether 33 identical `usage()` definitions is a real
maintenance problem or just how shell gets written is a judgement, and the
judgement is arguable.

## Pros

- ~400–600 lines, and one definition of the output convention instead of 33.
- A fix to the usage format lands everywhere at once.
- New commands stop re-deciding how to print help.

## Cons

- **Sourcing a library adds a failure mode.** A broken `omarchy-lib.sh` breaks
  every command that sources it, at once, instead of one command being wrong.
  For 400 lines that is a poor trade.
- It adds a dependency to scripts that currently have zero. Omarchy's commands
  being self-contained is a genuine property, not an accident.
- 33 identical `usage()` functions is what shell looks like. It is not a defect
  the way four panels re-implementing a fetch cache is a defect.
- Nothing enforces the library, so the 34th command will not use it. This
  needs a lint rule to hold, and a lint rule is a new thing to maintain.

## Risk

**Low, and the failure is loud** — a broken library breaks many commands
visibly, not subtly.

The subtler risk is the drift: the library exists, the convention is nice, and
nothing enforces adoption, so the duplication grows anyway and now there are
two ways to print help.

## Evidence

```bash
# the duplication, by function
cd /usr/bin && grep -hoE '^[a-z_][a-z0-9_]*\(\)' omarchy* | sort | uniq -c | sort -rn | head -25

# and nothing shares anything today
grep -lE 'source .*omarchy-lib|\. .*omarchy-lib' /usr/bin/omarchy* | wc -l   # 0

# what a usage() actually looks like, in a couple of them
grep -A6 '^usage()' /usr/bin/omarchy-theme-set /usr/bin/omarchy-plugin-list
```

## Amendment history

- 2026-09-30 — initial record.