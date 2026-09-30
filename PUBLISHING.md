# Publishing this knowledge base

**Already done.** The repository is live, configured, and pushed. This file is
kept as the record of what was set up and what a fork or a re-publish would
need to repeat.

Live at **<https://github.com/Sleepy-Studio/omarchy-reduction>** (public, org
`Sleepy-Studio`).

## What is configured

| | state |
|---|---|
| Repository | `Sleepy-Studio/omarchy-reduction`, public |
| Default branch | `main`, tracking `origin/main` |
| Discussions | enabled, default categories including **Q&A** (`q-a`) |
| Issue intake | three forms; `blank_issues_enabled: false` |
| Labels | `measurement-appeal`, `amendment`, `new-record` |
| Licence | CC BY-SA 4.0 |

The `OWNER/REPO` placeholders in `.github/ISSUE_TEMPLATE/config.yml` have been
replaced with the real URLs, so the "Ask a question" link resolves.

## The labels trap

The three issue forms each apply a label. **If a label does not exist, GitHub
discards it silently** — no warning, no error. The issue is created without it
and intake quietly stops being filterable.

All three now exist. If you ever recreate the repo, create the labels *before*
enabling the issue templates.

## Verifying

```bash
bash run-tests.sh
```

Must be green (12 passed, 0 failed).

Then, on a **copy**, confirm the safety gate still refuses to run an unsafe
measurer:

```bash
T=$(mktemp -d); cp -r . "$T"/
printf '\nomarchy theme set nord\n' >> "$T"/tools/measure.py
(cd "$T" && bash run-tests.sh)   # must FAIL at step 0
rm -rf "$T"
```

## What must never be committed

- Anything from `~/.config`, other projects, or shell history.
- Machine-identifying data. `run-tests.sh` step 4 fails on `/home/<name>` and
  `/root` paths in `baseline/`, which is why that gate exists — the baseline is
  public.
- PIDs. `measure.py` aggregates per program name precisely so a committed
  baseline stays reproducible on someone else's machine.

## What a PR must not contain

No patch to the installed system. No change outside this repository. No edits
under `/usr/bin`, `/usr/share/omarchy`, or `~/.config/omarchy`, no theme
changes, no shell restart, and no `omarchy` subcommand that writes.

This repository documents; it does not act. Acting on a record is a patch to
Omarchy, and that belongs somewhere else.

## The one number that will not match

The records were measured on an **edge/dev channel** Omarchy build. A reader on
stable will see different *structural* numbers — command count, line counts,
plugin count — and file a measurement appeal that is not really one. Worth a
line in the README before wide circulation; see
[KB-011](knowledge-base/findings/KB-011-dispatcher-cost.md) for why the timing
figures are single-machine regardless.