---
id: KB-011-dispatcher-cost
title: Every omarchy command pays ~45 ms to rebuild its own routing table
type: measurement
status: accepted
strength: strong
surface: commands
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

`omarchy version` takes about **45 ms**. It answers from two `pacman -Q`
calls. The other ~44 ms is the dispatcher re-deriving a routing table that
could have been derived once.

`/usr/bin/omarchy` is a **1,091-line** bash script. On every invocation it:

- globs every `omarchy-*` — 445 files,
- reads up to `METADATA_SCAN_LIMIT=80` lines of each header,
- parses `summary`, `group`, `args`, `examples`, `alias`/`aliases`, `hidden`,
  `requires-sudo`,
- builds roughly fifteen associative arrays and a collision-checked route
  table,
- resolves the route and `exec`s the real binary.

Measured on this machine: `omarchy version` ≈ **45 ms**, `omarchy theme list`
≈ **11 ms**. The difference between the two is the cost of the work they
actually do; the ~45 ms floor is the scan.

**This has already been optimized once.** `METADATA_SCAN_LIMIT=80` exists,
and the route table detects collisions with a `ROUTE_COLLISIONS` array. The
author knew the cost was real and bounded it. It is still 44 ms on the
cheapest command in the system.

The command metadata is already **declarative** — comments in a header block,
present on 443 of 445 commands. The system re-parses its own declaration on
every run.

## Proposal

**Measure and publish the cost — which is what this record is.**

The reduction is [KB-021](../KB-021-prebuilt-command-index.md): build the
table once into an index file, with a fallback to the full scan when the index
is missing or stale.

The measurement matters on its own for a reason beyond "it could be faster":
it quantifies what every omarchy invocation costs, which is a number nobody
currently knows. 45 ms is invisible one at a time and material when a menu
search or a panel refresh loops over commands.

## Pros

- Turns an unremarked constant into a measured one. That is the main value of a
  measurement record.
- Identifies the cost as *fixed overhead*, not per-command work — which is why
  it does not show up when anyone profiles a specific slow command.
- Explains an existing design decision rather than criticising it. The scan
  limit and collision detection are evidence the author was optimising within
  the constraint "no build step", which is a real constraint for a system
  installed from packages.

## Cons

- **45 ms on one machine is not 45 ms everywhere.** The scan is
  filesystem-bound: 445 file opens in a directory. On a slower disk, on a
  spinning drive, on a heavily loaded system, or on a network filesystem, it is
  materially worse. A single measurement understates the range.
- **The absolute numbers are small enough that the benefit may not be real.** If
  a person invokes an omarchy command a few times a minute, 45 ms is
  unnoticeable. The reduction only pays off where commands are invoked in a
  loop — a menu search, a panel, a hook. Nobody has established which of those
  exist and how often they run, so the benefit is unquantified.
- **It has been optimized once already.** A second optimisation is only worth
  it if the first did not solve it, and the author's choice of a scan limit
  over a generated index may have been deliberate — a generated index has to be
  regenerated, and a stale index is a bug.
- **The measurement is a warm-cache measurement.** These numbers come from a
  loop, which is the best case. First invocation after boot is worse and is not
  what was measured.

## Risk

**Low as a measurement.**

The risk is treating a single-machine, warm-cache number as a system-wide
constant. The honest claim is "tens of milliseconds of fixed overhead per
invocation on this machine"; anything stronger is not supported.

That risk is why this record states its own limits rather than letting the
number travel.

## Evidence

```bash
# the cost, on your machine
for c in version "theme list" "plugin list"; do
  s=$(date +%s%N); omarchy $c >/dev/null 2>&1; e=$(date +%s%N)
  echo "$(( (e-s)/1000000 ))ms  omarchy $c"
done

# cold vs warm — the difference is the part not measured above
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null 2>&1   # if allowed
s=$(date +%s%N); omarchy version >/dev/null 2>&1; e=$(date +%s%N)
echo "cold: $(( (e-s)/1000000 ))ms"

# the scan, in the source
sed -n '1,10p'    /usr/bin/omarchy     # METADATA_SCAN_LIMIT
sed -n '310,360p' /usr/bin/omarchy     # the glob
sed -n '185,240p' /usr/bin/omarchy     # the header parse

# how much there is to parse
grep -c 'omarchy:summary' /usr/bin/omarchy* | grep -c ':1$'   # 443

# and the collision detection that shows it was already thought about
grep -n "ROUTE_COLLISIONS" /usr/bin/omarchy
```

## Amendment history

- 2026-09-30 — initial record.