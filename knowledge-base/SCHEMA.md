---
id: KB-SCHEMA
title: The record schema
type: schema
status: living
---

# Record schema

Every finding in `knowledge-base/` is one file in `knowledge-base/findings/`
with this exact shape. It exists so that a stranger can amend one record
without reading the others, and so that disagreement is visible rather than
buried in prose.

`run-tests.sh` step 3 validates every record against this schema. If a record
does not validate, the suite fails — so a malformed amendment cannot land.

## Frontmatter

```yaml
---
id: KB-NNN-slug          # stable, unique, never reused. This is the anchor
                         # that survives the record being rewritten.
title: One line         # imperative, specific
type: reduction | defence | open-question | measurement
status: proposed | accepted | implemented | rejected | superseded
strength: strong | moderate | speculative
surface: >              # what it touches
  commands
confidence: high | medium | low
measuredOn: YYYY-MM-DD  # when baseline/ was generated for this record
supersedes: KB-NNN      # optional
amendedBy: <github-handle>   # optional; set by hand, not generated
amendments: N           # substantive amendments by others so far. A fresh
                         # record is 0 and has exactly one history line
                         # ("initial record"). Bump it only when you change
                         # substance, not wording. The validator checks this
                         # against the history.
---
```

`status` and `strength` are deliberately separate. A record can be
`proposed` with `strong` evidence, or `accepted` on `speculative` reasoning —
and the second one is the thing worth arguing about in review.

## Body sections

All seven are required, in this order. Empty is allowed; missing is not.

### `## Problem`

The measured fact, with the number and where it came from. Must be
re-checkable against `baseline/measurements.json` on the record's
`measuredOn`. No argument here — just what is true.

### `## Proposal`

What should change, specifically enough that someone could disagree with it.
Named files, named counts, named mechanisms. "Refactor the panels" is not a
proposal.

### `## Pros`

The case for. Include the strongest version of it, not the safe one.

### `## Cons`

The case against, from someone who wants to keep things as they are. This
section is the point of the whole knowledge base: a reduction whose cons are
soft is not ready to be accepted.

### `## Risk`

What breaks, how likely, and how it would be noticed. Distinguish "breaks
loudly" from "silently wrong", and prefer proposals where failure is loud.

### `## Evidence`

How to verify this claim yourself, on your own machine. Commands, file paths,
line references. Anyone must be able to check it without trusting the author.

### `## Amendment history`

One line per substantive change: date, handle, what changed and why. Do not
edit earlier lines — that is what makes the history trustworthy.

## Vocabularies

`type`:
- `reduction` — something could be smaller or simpler
- `defence` — something looks reducible and should NOT be. Also a finding.
- `open-question` — unresolved; needs investigation or upstream discussion
- `measurement` — a measured fact with no recommendation attached

`status`: see frontmatter.

`strength`:
- `strong` — the measurements support it and the argument is sound
- `moderate` — the measurements support it; the proposal is debatable
- `speculative` — plausible from reading the source, not yet measured

`confidence`:
- `high` — verified by `run-tests.sh` against the committed baseline
- `medium` — verified once by hand, may drift
- `low` — reasoned from source reading only

## Rules

1. **A record never states an unmeasured number as fact.** Either cite
   `baseline/measurements.json` or mark it speculative.
2. **`defence` records are first-class.** This knowledge base will look
   foolish if it is only a list of things to change. Most of what is hardest to
   improve in Omarchy is hardest for a reason, and saying so is a finding.
3. **Disagreement goes in the record, not in a new file.** If you disagree
   with a proposal, amend that record's `## Cons` and say so in the history.
4. **`status: rejected` is a good outcome.** Recording why a plausible
   reduction was rejected stops the next person re-proposing it.
5. **No implementation.** These records describe. Nothing in this repository
   changes the behaviour of the installed system.