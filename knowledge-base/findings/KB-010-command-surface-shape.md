---
id: KB-010-command-surface-shape
title: 445 commands, and the shape that suggests where the depth is
type: measurement
status: accepted
strength: strong
surface: commands
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

The command surface is **445 commands across 34,842 lines of bash**, in 22
documented groups.

Size distribution:

| bucket | count |
|---|---|
| ≤15 lines | **136** |
| 16–60 | 173 |
| 61–300 | 116 |
| >300 | 20 |

74 commands are `hidden`. 443 of 445 carry `omarchy:summary` metadata — the
declarative header is near-universal, which is worth knowing because it means
the command surface is already machine-readable in principle.

The families that matter are the ones where a *verb* is encoded in the name
rather than in an argument:

| family | count |
|---|---|
| `restart-*` | 17 |
| `theme-set-*` | 16 |
| `install-gaming-*` | 9 |
| `remove-gaming-*` | 9 |
| `install-service-*` | 8 |
| `hyprland-window-*` | 7 |

`omarchy install-gaming-gpu-nvidia` and `omarchy install gaming gpu nvidia` are
the same decision at two altitudes. So are 18 gaming commands that are one verb
with a sign, and 17 `restart-*` targets that are one command with an argument.

## Proposal

**Measure and publish the shape — which is what this record is.**

The reduction that follows from it is [KB-022](../KB-022-argument-dispatch-collapse.md),
and the honest framing matters more than the number:

**Reduce depth, not breadth.** The command *count* is what makes
`omarchy <thing>` discoverable through `omarchy commands` and through the
menu, and that discoverability is worth real money. Collapsing
`install-gaming-*` and `install-gaming-*` into one command makes the surface
*narrower*; collapsing the 136 thin commands into a table-backed command makes
it *shallower* without removing a single name.

The 136 thin commands are the strongest signal here and the least discussed:
most are three lines of argument parsing and one call. That is a declarative
command wearing the costume of a script.

## Pros

- Anyone reasoning about the command surface can start from the distribution
  rather than from intuition.
- The family names make the depth problem visible without needing an
  argument.
- The size buckets separate "many commands" from "much code" — 445 commands is
  not the same problem as 34,842 lines, and only the second is about
  duplication.

## Cons

- **The distribution does not imply a defect.** A large command surface with
  many small commands is what a CLI with good coverage looks like. 136 commands
  under 15 lines is only remarkable if they duplicate each other, which this
  measurement does not establish — only one byte-identical pair was found
  ([KB-025](../KB-025-duplicate-command-bodies.md)).
- **22 groups is fewer than the 78 the sibling project `homelpy` measures.**
  Those are different units: 78 top-level path segments there, 22 declared
  `omarchy:group` values here. Anyone quoting either number should say which.
- The families are counted by name prefix, which is a heuristic. `restart-*`
  being 17 files does not mean they are all argument dispatch — some
  genuinely do different things.
- Publishing a distribution invites a conclusion it does not support. "136 thin
  commands" reads as an accusation until you have checked for duplication.

## Risk

**Low as a measurement; the risk is in the reading.**

A measurement record can do damage by being cited without its caveats. The
caveat that matters: this shows shape, not waste. Treating the 136 thin
commands as a defect without first measuring how many are genuinely redundant
is how a plausible refactor acquires a false justification.

## Evidence

```bash
# the distribution and the families
python3 -c "
import json; d=json.load(open('baseline/measurements.json'))['commands']
print('count', d['count'], 'lines', d['linesTotal'])
print(d['sizeBuckets'])
print('hidden', d['metadata']['hidden'])
print(*d['largestFamilies'], sep='\n')
print(*d['largest'], sep='\n')"

# how metadata-declared it is
grep -c 'omarchy:summary' /usr/bin/omarchy* | grep -c ':1$'

# the declared groups
grep -hoE '^# omarchy:group=\S+' /usr/bin/omarchy* | sort -u

# is a thin command actually redundant? compare two
cat /usr/bin/omarchy-theme-list /usr/bin/omarchy-version
```

## Amendment history

- 2026-09-30 — initial record.