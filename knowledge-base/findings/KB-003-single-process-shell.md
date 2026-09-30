---
id: KB-003-single-process-shell
title: One process for the whole desktop is the right architecture
type: defence
status: accepted
strength: strong
surface: shell
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

The entire desktop shell — bar, panels, overlays, menus, the menu itself, the
lock screen — is **one `quickshell` process** carrying roughly 35,000 lines of
QML and 4,800 lines of JS. Measured anonymous memory is around **427 MB**.

35,000 lines in one process is the kind of number that reads as a problem. The
reflex is to split it: one process per panel, an IPC bus between them, smaller
units that can be restarted independently. That is the obvious reduction in
*blast radius* and it would make the system strictly worse.

## Proposal

**Keep it as one process.** Splitting per-panel is the naive refactor, and the
cost of it is not obvious until you count.

Omarchy already solved the "restart one thing without restarting everything"
problem a better way: `omarchy restart <target>`, and panels that load and
unload through a registry of `Loader`s. `shell.qml` holds one `Loader` per
discoverable panel/overlay/menu plugin, active only when the host marks it
open. The isolation you would get from separate processes is already there, at
a fraction of the cost.

## Pros

- **No IPC surface.** Panels talk to each other by property access and signals
  in one object tree. A per-panel process architecture needs a protocol, a
  protocol version, and a failure story for "the other side went away".
- **No startup cost multiplier.** One Quickshell init, one QML engine, one
  warm cache. Ten processes means ten engine starts on every login.
- **Shared state is free.** The bar, the panels, and the menu genuinely share
  state. Across processes that becomes copies with synchronisation.
- **Theme changes are instant**, because the shell is the thing being changed.
  Across processes, every panel needs telling, and any that misses it keeps the
  old palette until restarted.
- A cross-panel bug is debuggable in one process with one stack trace. Across
  processes it is a distributed-systems problem.

## Cons

- **One process means one crash takes the whole desktop shell.** A bad
  `Panel.qml` can take the bar, the menu, and the lock screen with it. Separate
  processes would contain that.
- **~427 MB of anonymous memory in one process is not modular memory.** It
  grows, and nothing in the architecture bounds it. A panel that leaks is not
  identifiable because everything shares an address space.
- **The registry and the routing in `shell.qml` (1,744 lines) is the coupling
  that a process boundary would remove.** If the shell keeps growing
  coordination logic, the single process becomes a genuine bottleneck rather
  than a deliberate choice.
- Nothing measures whether that growth is happening. The architecture is
  defensible, but "defensible in principle" is not the same as "still true at
  60,000 lines".

## Risk

**Low to reverse; moderate to introduce.**

Splitting the shell is a large, invasive change that touches every panel, and
its failure mode is not a crash — it is a system that is subtly harder:
cross-panel behaviour that used to be a property access becomes a round trip,
and any latency or ordering bug it introduces will be intermittent and very
hard to attribute.

The real risk is that splitting is *plausible* rather than necessary, so it gets
done during some unrelated refactor and nobody measures the cost afterwards.

## Evidence

```bash
# it really is one process
ps -C quickshell -o pid,rss,comm
python3 -c "
import json; d=json.load(open('baseline/measurements.json'))
print(*d['runtime']['programs'], sep='\n')"

# the shell's own size, and the largest files in it
python3 -c "
import json; d=json.load(open('baseline/measurements.json'))['shell']
print(d['qmlLines'], 'QML lines in', d['qmlFiles'], 'files')
print(*d['oversized'][:6], sep='\n')"

# the mechanism that already gives per-panel isolation
grep -n "Loader\|active:" /usr/share/omarchy/shell/shell.qml | head -30

# panels are loaded on demand, not at startup
grep -n "on summon\|onSummon\|keepLoaded" /usr/share/omarchy/shell/shell.qml | head
```

To establish the fourth con — whether the coordination logic is growing faster
than the system — this needs a time series of `shell.qml` and
`PluginRegistry.qml` line counts across Omarchy versions. Nobody has that yet.

## Amendment history

- 2026-09-30 — initial record.