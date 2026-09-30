---
id: KB-022-argument-dispatch-collapse
title: Collapse the argument-dispatch commands into one command each
type: reduction
status: proposed
strength: moderate
surface: commands
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

Some of the 445 commands are argument dispatch wearing the costume of
separate commands.

Measured families (`baseline/measurements.json` → `commands.largestFamilies`):

| family | commands |
|---|---|
| `restart-*` | 17 |
| `theme-set-*` | 16 |
| `install-gaming-*` | 9 |
| `remove-gaming-*` | 9 |
| `install-service-*` | 8 |
| `hyprland-window-*` | 7 |

`omarchy install-gaming-gpu-nvidia` and `omarchy install gaming gpu nvidia`
are the same decision at two altitudes. So are 18 gaming commands that split
into install/remove halves of one verb, and 17 `restart-*` targets that are one
command with an argument.

The dispatcher already understands both forms — it routes on
`omarchy-<group>-<sub>-<sub>` as well as on space-separated words. The
verbosity is not required by the routing; it is a convention nobody revisited.

The thin end of the same distribution: **136 of 445 commands are ≤15 lines**.
Most of those are argument parsing and one call. That is a *declarative*
command wearing the costume of a script.

## Proposal

Reduce **depth**, not breadth. The count is what makes `omarchy <thing>`
discoverable through `omarchy commands`, and that discoverability is worth
real money — it is not the thing to save.

- `install-gaming-*` + `remove-gaming-*` → one command with a verb.
  **18 files → 2.**
- `restart-*` → `omarchy restart <target>`, with no argument listing the
  targets. **17 → 1.**
- The 136 thin commands → one generated command whose body comes from a
  table. Each is 3 lines of argument parsing plus one call; the table is a
  more honest description of what they are.

**Do this as a generated change, never as 136 hand edits.** The table is
generated from the existing files, and the compatibility shims that keep every
existing `omarchy X Y` invocation working are generated too. Hand-editing 136
files is where the blast radius becomes real.

## Pros

- Fewer files to maintain, one place to change a convention.
- Removes ~18 + ~16 files outright in the two clearest families.
- The generated-table form makes the argument convention *uniform*, instead of
  136 separate interpretations of it.
- Depth reduction is invisible to muscle memory: `omarchy restart shell`,
  `omarchy theme set foo` keep working, because the shims stay.

## Cons

- **This is the largest blast radius in the knowledge base.** It touches
  every keybind, menu entry, hook, and script that invokes any of these
  commands. A missed shim is a broken keybind the user discovers by pressing
  it.
- The generated form is less readable than 136 small scripts. Someone
  debugging `omarchy theme set` now reads a table plus a generic driver.
- 20 commands are >300 lines (see `largest` in the measurements) and some of
  those are in these families — a thin shim wrapper over a large body is
  mechanical, but a *generated* one risks obscuring real logic.
- It is a lot of churn for a codebase that currently works. Churn has a cost
  that does not appear in any measurement here.

## Risk

**Highest of any record here, and the reason `strength` is `moderate` rather
than `strong`.**

The failure mode is the bad one: not loud, but **silently wrong**. A keybind
that no longer resolves looks like an Omarchy bug. A menu entry that no longer
resolves looks like a broken menu. Neither points at the refactor.

Mitigations that would have to be in place first:

- The shim set is generated from the *current* command list, so it is provably
  complete before anything is removed.
- A test that every name in the current 445 still routes, checked against the
  index from KB-021. That test is the real safety net, and it is only possible
  once KB-021 exists.
- The large commands are excluded from the mechanical pass.

## Evidence

```bash
# the families
python3 -c "
import json; d=json.load(open('baseline/measurements.json'))['commands']
print(*d['largestFamilies'], sep='\n')"

# the thin majority
python3 -c "
import json; print(json.load(open('baseline/measurements.json'))['commands']['sizeBuckets'])"

# what would need to keep working
omarchy commands --all | sed -n '/^Aliases:/,$p'
grep -rn 'omarchy ' ~/.config/hypr/bindings.lua | head -30

# the large commands to exclude
python3 -c "
import json; d=json.load(open('baseline/measurements.json'))['commands']
print(*d['largest'], sep='\n')"
```

## Amendment history

- 2026-09-30 — initial record.