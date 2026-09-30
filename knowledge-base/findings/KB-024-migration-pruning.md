---
id: KB-024-migration-pruning
title: Stop shipping migrations that can no longer be needed
type: reduction
status: proposed
strength: moderate
surface: updates
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

**106** migration scripts ship in `/usr/share/omarchy/migrations/`, named by
unix timestamp. Each runs once. None are ever removed.

The state directory `~/.local/state/omarchy/migrations` records what has run,
so the mechanism knows. Nothing acts on it.

At the observed rate this is a few hundred scripts within a couple of years,
and every one is a file the package carries, that a maintainer reads, and that
`omarchy-migrate --pending` has to consider on every login.

## Proposal

**Not** "delete migrations this machine has run." That is the tempting version
and it is wrong — see the risk section, which is the reason this record is
`moderate` and not `strong`.

The correct shape is a **support-window deletion**: a migration may be removed
when the oldest state it can still serve is no longer a supported upgrade
starting point. That is a packaging decision about the supported upgrade
window, not a per-machine one, and it belongs upstream.

So this record is not really a patch. It is a statement that the growth is
real and that the fix is a policy rather than a mechanism.

What is actionable here, without an upstream decision:

- Measure the growth (done — 106).
- Record the state directory as the place that knows what has run.
- Ask the question upstream: what is the oldest supported upgrade starting
  point, and does anything delete migrations older than that?

## Pros

- Unbounded growth with a real ceiling, in a directory every update touches.
- Cheap: deleting a script no longer in the support window has no
  behavioural effect by definition.
- It shrinks the package and shortens the pending-check on every login.

## Cons

- **The decision is not ours to make.** Deleting a migration someone still
  needs turns a working upgrade into a broken one, and the failure surfaces
  on *their* machine, not ours.
- The support window is a policy the maintainers may not want to state
  precisely, in which case the growth is a deliberate trade rather than an
  oversight.
- A migration can have side effects a later version re-does differently.
  Deleting the old one removes the record of *why* the newer one looks the way
  it does, which is a real loss of institutional knowledge.

## Risk

**High if done per-machine, low if done as a support-window policy.**

The per-machine version — "delete what has run here" — is actively dangerous:
a machine three versions behind upgrades in one jump and finds the migrations
it needed are gone. That failure is loud, but it happens on someone else's
hardware at an inconvenient moment.

The support-window version is safe by construction, and has no downside beyond
being someone else's decision to make.

## Evidence

```bash
ls /usr/share/omarchy/migrations | wc -l        # 106

# the earliest and latest — the width of the window we ship for
ls /usr/share/omarchy/migrations | sort | sed -n '1p;$p'

# what ran here, which is known and unused for pruning
ls ~/.local/state/omarchy/migrations | head

# the pending check that runs on every login
grep -n "pending_migrations\|--pending" /usr/bin/omarchy-migrate /usr/bin/omarchy-migrate-notify
```

The question to ask upstream: **what is the oldest state an Omarchy install
can upgrade from, and is anything deleting migrations older than that?**

## Amendment history

- 2026-09-30 — initial record.