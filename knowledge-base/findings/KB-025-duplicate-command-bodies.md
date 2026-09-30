---
id: KB-025-duplicate-command-bodies
title: Two command names share one body, and one of them is probably wrong
type: reduction
status: proposed
strength: strong
surface: commands
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

`omarchy-nvim-refresh` and `omarchy-nvim-setup` are **byte-identical**
(`baseline/measurements.json` → `commands.duplicateBodies`).

A byte-identical pair under two names is not a design. It is one of:

- an alias that was never declared as one, so it appears twice in
  `omarchy commands --all` and in the menu,
- a copy-paste where one of them was meant to do something else,
- a leftover after a rename.

Which of those it is, is not knowable from this repo — it needs someone who
knows what nvim setup is supposed to do.

Only 2 of 445 commands lack `omarchy:` metadata entirely, and this pair is a
clean duplicate by content, so this is genuinely the only one of its kind.

## Proposal

Determine which of the three names is authoritative, then:

- if they are genuinely the same operation, declare one an **alias** so the
  dispatcher lists it once and the route table stops carrying two entries;
- if they were meant to differ, implement the difference.

The alias route is a one-line frontmatter change — `# omarchy:alias=...` —
which the existing metadata system already supports.

## Pros

- Trivial in every dimension: one line, one file, no blast radius.
- Removes a duplicate from `omarchy commands --all`, which is a list a person
  reads. One fewer line of noise in the largest list in the system.
- Duplicate names hide real mistakes. If `nvim-setup` was supposed to differ
  from `nvim-refresh`, that is a latent bug that is invisible precisely
  because the two are identical.

## Cons

- Almost nothing. The only real cost is that finding out which is correct
  needs a maintainer or someone who uses the nvim integration.
- If both names are depended on by a keybind, the alias has to keep both
  resolvable — which the alias mechanism does, so this is a non-issue.

## Risk

**Very low, and loud.**

Changing one to an alias cannot break anything that works today, because
today they are the same program. The only way to break something is to
implement a difference, which is the branch that needs the answer first.

## Evidence

```bash
# the duplicate
diff /usr/bin/omarchy-nvim-refresh /usr/bin/omarchy-nvim-setup && echo IDENTICAL
md5sum /usr/bin/omarchy-nvim-{refresh,setup}

# and the general check, which should stay empty
python3 -c "
import json; print(json.load(open('baseline/measurements.json'))['commands']['duplicateBodies'])"

# does anything invoke either name
grep -rn 'nvim-refresh\|nvim-setup' ~/.config/hypr/ /usr/share/omarchy/default/ 2>/dev/null
```

## Amendment history

- 2026-09-30 — initial record.