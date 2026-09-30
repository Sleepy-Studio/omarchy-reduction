---
id: KB-013-panel-data-models
title: Ten panel models, no shared data layer
type: measurement
status: accepted
strength: strong
surface: shell, plugins
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

Ten panels, each shipping a `Model.js`:

| model | lines |
|---|---|
| `network` | 380 |
| `tailscale` | 325 |
| `clock` | 296 |
| `weather` | 295 |
| `audio` | 262 |
| `bluetooth` | 177 |
| `dropbox` | 137 |
| `monitor` | 124 |
| `power` | 104 |
| `wifiqr` | 37 |
| **total** | **2,137** |

The panel structure itself is right: a `Panel.qml` plus a `Model.js`, consistent
and independently readable. What is missing is a layer underneath. Each model
independently re-implements the same four things:

1. a fetch-and-parse cycle,
2. a cache with a staleness check,
3. a "only while the panel is open" guard,
4. an error path that keeps the last good value.

There is nothing to reach for. `qs.Commons` contains exactly four singletons —
`Color`, `Style`, `Border`, `Util` — and **all four are presentational**. The
system's shared layer is entirely about how things look, with nothing beneath
it for how they fetch.

The same duplication appears in the timer wiring: the weather panel declares
10 `Timer`s, bluetooth 10, network 9, each managing the same open/close
lifecycle by hand.

## Proposal

**Measure and publish the duplication — which is what this record is.**

The reduction is [KB-023](../KB-023-shared-polling-primitive.md): one
`CachedPoll` in `qs.Commons`.

Keeping them apart matters because the measurement is what a reader needs in
order to disagree with the reduction. Someone who reads only "ten models, no
shared layer" is likely to over-read it; someone who reads the four-item list
can see that only four of the ten actually match the pattern.

## Pros

- Establishes that the duplication is real and quantified, rather than a vague
  sense that panels repeat themselves.
- Shows the shape of the gap precisely: `Commons` is presentational-only. That
  is a description of an architectural boundary, which is more useful than a
  line count.
- Names which models are genuinely large. `network` at 380 lines is doing real
  work; `wifiqr` at 37 is not the same kind of thing at all.

## Cons

- **The duplication is unquantified.** This record counts lines and shows the
  shape, but it does not establish how many lines are the *repeated* four
  items versus panel-specific domain logic. The 300–400 line estimate in KB-023
  is an estimate, and nobody has done the comparison that would make it a
  measurement.
- **Ten panels with ten models may be correct.** Independent models are
  independently modifiable. If the shared primitive is designed from four call
  sites, it is a guess at the other six, and a wrong guess is worse than the
  duplication.
- **The line counts are not comparable.** `network` at 380 and `wifiqr` at 37
  are both "a Model.js" and neither figure says anything about complexity.
- A `Commons` that mixes presentational and data singletons is a different kind
  of module from the one that exists now, and that is a design change nobody
  has asked for.

## Risk

**Low as a measurement.**

The risk is that a count of lines gets read as a count of waste. The honest
claim is: ten models exist, none shares a lifecycle, and `Commons` has nothing
for them to share. Whether that should change is KB-023's argument, not this
record's fact.

## Evidence

```bash
# the models, by size
find /usr/share/omarchy/shell/plugins/panels -name Model.js -exec wc -l {} + | sort -n

# what Commons provides — four singletons, all presentational
ls /usr/share/omarchy/shell/Commons
cat /usr/share/omarchy/shell/Commons/qmldir

# the repeated timer lifecycle, per panel
grep -c 'Timer' /usr/share/omarchy/shell/plugins/panels/*/Panel.qml | sort -t: -k2 -rn

# what one model's error and cache handling actually looks like
sed -n '1,90p' /usr/share/omarchy/shell/plugins/panels/network/Model.js
sed -n '1,60p' /usr/share/omarchy/shell/plugins/panels/wifiqr/Model.js

# and that no shared data primitive already exists anywhere
grep -rl "CachedPoll\|PollingModel" /usr/share/omarchy/shell/ || echo "none"
```

## Amendment history

- 2026-09-30 — initial record.