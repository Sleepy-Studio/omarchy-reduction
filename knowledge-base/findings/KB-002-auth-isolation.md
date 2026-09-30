---
id: KB-002-auth-isolation
title: Three auth mechanisms, not one — do not collapse them
type: defence
status: accepted
strength: strong
surface: shell, plugins
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

Authentication isolation in the shell is implemented three times over. That
looks like redundancy, and redundancy is the thing reduction proposals usually
target first.

The shell README is unusually direct about it:

> Authentication capabilities are stamped from trusted first-party manifests,
> authentication services are retained outside the host's public service map
> and QML object tree, and changing a third-party registry or configuration
> snapshot cannot mutate host state.

Three mechanisms, because one was not enough:

1. **Capabilities are stamped from trusted manifests only.** A manifest cannot
   declare its own capabilities — there is no `capabilities` key that a
   third-party plugin can set and have honoured.
2. **Auth services live outside the public service map** and outside the QML
   object tree, so a facade lookup simply does not find them.
3. **Config snapshots are detached copies**, so mutating one cannot write
   through to host state.

Mechanism 2 in particular is not a check that can be bypassed by writing better
code — it is an *absence*. The service is not reachable to be found.

## Proposal

**Do not collapse them.** If the argument is ever made to reduce three to two,
the question to ask is which one is genuinely redundant, and the answer is
almost certainly none of them: they fail differently.

## Pros

Keeping all three is correct because each closes a different hole:

- A capability check that can be skipped by not being called (1).
- A lookup that finds nothing because the target is not there (2).
- A reference that cannot be mutated through (3).

The shell README also says this is the sharpest edge in the whole system,
which is a maintainer telling you they thought about it more than most
proposers have.

## Cons

- **Three mechanisms for one invariant is genuinely more to understand.** A
  future maintainer has to hold all three in their head to avoid breaking one,
  and the failure mode of understanding only two is a security hole.
- **Mechanism 1 is load-bearing and subtle.** A hand-written third-party plugin
  gets `[]` — no capabilities. You cannot self-declare your way to more
  access; you must be a clone. That is a sharp, non-obvious rule, and it is
  easy to break by "fixing" the manifest path to also read a plugin's own
  capabilities field.
- **There is no test asserting all three.** Each is argued in prose. Prose
  decays; assertions do not.
- If any one of the three is in practice redundant, that redundancy is a
  maintenance cost with no benefit — but nobody has established which, and
  guessing wrong in the direction of *removing* is the dangerous direction.

## Risk

**Highest consequence of any record in this knowledge base, and the least
visible.**

Collapsing the three does not break anything. Every plugin that works
continues to work. The boundary is simply gone, and the only signal is a
third-party plugin one day reaching an auth service it should not have — at
which point the shell README's claims are the thing that turns out to have
been wrong.

Reducing a security mechanism is the worst possible
benefit-to-risk trade available in this repository, which is why the record
exists.

## Evidence

```bash
# the three mechanisms, in the source
grep -n -i -B2 -A8 "capabilities\|public service map\|snapshot" \
  /usr/share/omarchy/shell/README.md

# capability stamping — where a manifest's capabilities come from
grep -rn "__hostCapabilities\|stampHostCapabilities\|clonedFrom" \
  /usr/share/omarchy/shell/services/PluginRegistry.qml

# which services are withheld from the public map
ls /usr/share/omarchy/shell/services/

# the honest statement, from the source itself
grep -n -i "not a QML sandbox" -r /usr/share/omarchy/shell/
```

To establish whether one of the three is redundant: instrument a third-party
plugin that tries each path in turn and record which ones fail. That has not
been done.

## Amendment history

- 2026-09-30 — initial record.