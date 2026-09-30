---
id: KB-014-migrations-unbounded
title: 106 migrations ship, and none are ever deleted
type: open-question
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
so the mechanism knows. Nothing acts on it, and the scripts stay on disk
forever.

This is genuine unbounded growth with a real ceiling: every script is a file the
package carries, a maintainer reads when reviewing an update, and
`omarchy-migrate --pending` has to consider on every login.

**Why it is genuinely hard** — and why the obvious fix is wrong:

A migration that has run on *this* machine may still be needed by someone
upgrading from a much older state. Deleting a script because this machine ran
it turns a working upgrade into a broken one, on someone else's hardware, at an
inconvenient moment. Deletion has to be keyed on "nobody can still need this",
which is a **support-window decision, not a per-machine one**.

## Proposal

This is an open question, so the proposal is *what would have to be known to
answer it*, not a fix:

1. **What is the oldest state an Omarchy install can upgrade from?** A stated
   supported upgrade window would make the rule mechanical: migrations older
   than the window can be dropped by the package that supersedes them.
2. **Does anything already prune?** `~/.local/state/omarchy/migrations` knows
   what has run and nothing appears to act on it — but nobody has established
   that, only that the scripts are still on disk.
3. **Is the growth deliberate?** A system with a 6-command update path and 106
   migrations may accept unbounded growth as the cost of never breaking an
   upgrade. If that is the trade, it is a trade, and it should be written down
   rather than inferred to be an oversight.

**Who could answer:** upstream maintainers, or anyone who knows the supported
upgrade window. This is not answerable from the installed source — it is a
policy question, not a code question.

## Pros

Naming the question is worth something on its own: it is the one place in this
knowledge base where the honest answer is "I do not know, and the person who
does is not me". Recording that stops a plausible-looking fix from being
proposed again with the same wrong reasoning.

- The growth is measured and reproducible: 106 files, a count anyone can check.
- The difficulty is structural, not incidental — it is inherent to what a
  migration is, not an implementation oversight.

## Cons

- **An open question in a knowledge base can become a permanent one.** Nothing
  here forces an answer, and an unanswered record is one more thing to read.
- The per-machine reading is the obvious one, and it is wrong. Recording the
  question without the difficulty is how a future reader proposes the dangerous
  version.
- 106 scripts is not alarming on its own. The real ceiling is unknown, because
  nobody has the rate — this is a projection, not a measurement.
- If the growth *is* deliberate, this record documents a non-problem, which has
  value but is not the same as resolving anything.

## Risk

**The risk here is a misreading, not a defect.**

An open question gets quoted as if it were a finding — "Omarchy never prunes
migrations" is true and reads like an accusation, when the actual state of
knowledge is "nobody knows whether that is intended, and the obvious fix would
be wrong".

That is why `status` is `proposed` and not `accepted`, and why the difficulty is
stated in the Problem section rather than buried.

## Evidence

```bash
# how many, and the window they span
ls /usr/share/omarchy/migrations | wc -l          # 106
ls /usr/share/omarchy/migrations | sort | sed -n '1p;$p'

# what ran here — the state nobody acts on
ls ~/.local/state/omarchy/migrations | head
ls ~/.local/state/omarchy/migrations | wc -l

# the pending check that runs on every login
sed -n '25,80p' /usr/bin/omarchy-migrate
grep -n "pending\|--pending" /usr/bin/omarchy-migrate-notify

# and the one that fires an autostart notification
cat /usr/bin/omarchy-migrate-notify
```

The question to ask upstream: **what is the oldest state an Omarchy install
can upgrade from, and does anything delete migrations older than that?**

## Amendment history

- 2026-09-30 — initial record.