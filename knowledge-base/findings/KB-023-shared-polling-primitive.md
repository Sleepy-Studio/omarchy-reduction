---
id: KB-023-shared-polling-primitive
title: Give the ten panel models one shared polling primitive
type: reduction
status: proposed
strength: moderate
surface: shell, plugins
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

The panels are the pattern working *well*: a `Panel.qml` plus a `Model.js`,
consistent, predictable, each independently readable. That part is right.

What is missing is a layer underneath. Ten models, **2,137 lines**
(`network` 380, `tailscale` 325, `clock` 296, `weather` 295, `audio` 262,
`bluetooth` 177, `dropbox` 137, `monitor` 124, `power` 104, `wifiqr` 37), and
each independently re-implements the same four things:

1. a fetch-and-parse cycle,
2. a cache with a staleness check,
3. a "only while the panel is open" guard,
4. an error path that keeps the last good value.

There is no shared primitive to reach for. `qs.Commons` has exactly four
singletons — `Color`, `Style`, `Border`, `Util` — and **all four are
presentational**. The system's shared layer is entirely about how things look,
with nothing underneath for how they fetch.

The same duplication shows up in the timer wiring: 10 `Timer`s in the weather
panel, 10 in bluetooth, 9 in network, each managing the same open/close
lifecycle.

## Proposal

Add one primitive to `qs.Commons` — a `CachedPoll` — that owns the lifecycle
and the failure behaviour: start polling when the panel opens, stop when it
closes, cache the last good value, survive a failed fetch, expose staleness.

The domain logic stays where it is. `network/Model.js` still knows how to parse
`iw`; it just no longer re-implements *when to call* and *what to do when it
fails*.

**Scope it to the four that genuinely match** — network, bluetooth, weather,
tailscale. The other six have different enough lifecycles that forcing them
through a shared shape would be the wrong kind of consistency.

## Pros

- Removes an estimated 300–400 lines across four files.
- **Uniform failure behaviour.** Right now each panel decides for itself what a
  failed fetch does. A shared primitive means "every panel keeps its last good
  value and marks itself stale" is true by construction rather than by four
  separate correct decisions staying correct.
- Shorter models, and a smaller surface for the kind of timer bug that is
  invisible without a visual debugger.
- It puts something non-presentational in `Commons`, which is currently a gap
  in the shared layer rather than a considered choice.

## Cons

- **A shared primitive is a shared bug.** Every panel that adopts it inherits
  its failure modes. Four panels currently work; consolidating them means one
  mistake now affects four surfaces instead of one.
- The four that match today may not match after a change to any one of them.
  A primitive designed from four call sites is a guess at the fifth.
- `Commons` is currently purely presentational, so this changes its character.
  A data-layer singleton in a presentation singleton module is a small
  architectural step that some would object to.
- It saves 300–400 lines out of 35,000. The ratio is unimpressive; the value is
  in the uniformity, not the count.

## Risk

**Moderate, and quiet.**

The failure mode is a panel that stops refreshing, or refreshes when closed.
That is visible to a user but invisible to every automated check in this
project — and appearance cannot be verified from here.

That asymmetry is the honest argument for the conservative scope. Adopting it
in four panels first means a mistake is four panels wrong, not ten. Widening
it later is incremental; narrowing it later is a revert under pressure.

## Evidence

```bash
# the duplication, by file
find /usr/share/omarchy/shell/plugins/panels -name Model.js -exec wc -l {} + | sort -n

# what Commons actually provides today — four singletons, all presentational
ls /usr/share/omarchy/shell/Commons
cat /usr/share/omarchy/shell/Commons/qmldir

# the repeated timer lifecycle
grep -c 'Timer' /usr/share/omarchy/shell/plugins/panels/*/Panel.qml | sort -t: -k2 -rn

# what a model's error path currently does, in one of them
sed -n '1,80p' /usr/share/omarchy/shell/plugins/panels/network/Model.js
```

## Amendment history

- 2026-09-30 — initial record.