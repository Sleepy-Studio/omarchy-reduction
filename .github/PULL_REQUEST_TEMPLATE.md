# Pull request

A knowledge base about Omarchy, not a fork of it. Every record describes,
argues, or measures. A PR that implements one of these records is the wrong
PR — see the last section.

## Which records are touched?

<!-- KB ids, one per line. "none — tooling/docs only" is a valid answer. -->

- KB-NNN

## What did you measure?

<!--
If any number changed, paste the output of `bash tools/measure.sh` from the
machine you measured on, plus your `omarchy version`. If nothing numeric
changed, say so and say what you read instead.
-->

```
$ omarchy version
$ bash tools/measure.sh
```

## Which schema fields changed, and why?

<!-- type / status / strength / confidence / surface / amendments. None is a valid answer. -->

- `status`: — (why)
- `strength`: — (why)
- `confidence`: — (why)
- `surface`: — (why)
- `amendments`: — (bump only for substance; a wording fix is not substance)

## Confirmations

- [ ] `bash run-tests.sh` passes on my machine. It validates every record
      against `knowledge-base/SCHEMA.md` and fails if the numbers in the prose
      no longer match `baseline/measurements.json`.
- [ ] No personal paths, hostnames, usernames, or other identifying data from
      my machine are in the diff. `baseline/` is generated from paths under
      `/usr` and `/etc`; if something identifying got in, it is not committed.
- [ ] I did **not** edit any earlier `## Amendment history` line. I appended
      one. The history is only worth reading if the earlier entries are
      immutable — rewriting one destroys the only record of what a previous
      contributor actually argued.
- [ ] I amended an existing record rather than opening a rival one. If I
      disagree with a proposal, the disagreement is in that record's
      `## Cons`.
- [ ] The claim does not depend on how something *looks*. This repository will
      not claim to verify appearance; a visual claim is marked unverified and
      left for a human to check.

## This PR must not implement anything

**No patch to the installed system. No change outside this repository.** If you
want to act on a record, that is a patch to Omarchy — upstream or local — and
it belongs in a different repository.

In practice this means: no edits under `/usr/bin`, `/usr/share/omarchy`, or
`~/.config/omarchy`; no theme changes; no shell restart, rescan, or reload; no
`omarchy` subcommand that writes. A PR that includes one of those is a PR
against a machine, not against a repository, and it will be declined no matter
how good the argument is.

The one exception the tooling allows is `tools/measure.py` and `tools/measure.sh`
— the measurer itself, when the measurement is wrong. Fix the measurer and
re-measure; **never hand-edit `baseline/measurements.json`**, which is
generated.

## Licence

Prose is CC BY-SA 4.0, so quote and adapt it with credit. Measurements are
facts about a system and freely reusable.
