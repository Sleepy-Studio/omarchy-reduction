# Contributing

The real guide is at the repository root: **[`CONTRIBUTING.md`](../CONTRIBUTING.md)**.

Read it before opening a PR. The short version:

1. **Read the record** you want to change — start at
   [`knowledge-base/INDEX.md`](../knowledge-base/INDEX.md).
2. **Measure it yourself.** Every claim has an `## Evidence` section with
   commands that reproduce it. If your number differs and it is a structural
   number, the record is wrong.
3. **Amend that record** — not a rival one. Bump `amendments`, append to
   `## Amendment history`, change the substance.
4. **`bash run-tests.sh`** — validates every record and checks the prose still
   matches the measurements.
5. **Open a PR** saying what you measured. Nothing here implements anything.

Questions that are not yet records belong in Discussions.
