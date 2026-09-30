# Publishing this knowledge base

The repository is complete and self-verifying. This file is the launch
checklist — the handful of things that must happen once, by a human, before
other people can contribute to it.

Nothing here has been done yet: there is **no git repository, no remote, and
no `gh` authentication** on this machine.

## 1. Create the repository

```bash
cd ~/Projects/omarchy-reduction
git init -b main
git add -A
git commit -m "Omarchy knowledge base: 17 records, measured and schema-validated"
```

Do **not** create a public repo from a template with a README or LICENSE —
this repository already has both, and a template's would conflict.

Enable **Discussions** in the repository settings. The issue forms link to it,
and `CONTRIBUTING.md` points people there for questions that are not yet
records.

## 2. Replace the OWNER/REPO placeholders

`.github/ISSUE_TEMPLATE/config.yml` contains two placeholder links that will
not resolve until they are substituted:

```
https://github.com/OWNER/REPO/discussions
https://github.com/OWNER/REPO/discussions/categories/q-a
```

After pushing, create that Q&A category in Discussions, then fix both URLs.

## 3. Create the labels — or the forms will drop them

This is the one step that fails silently.

The three issue forms each apply a label:

| form | label |
|---|---|
| `measurement-appeal.yml` | `measurement-appeal` |
| `record-amendment.yml` | `amendment` |
| `new-measurement.yml` | `new-record` |

**If a label does not exist, GitHub discards it.** No warning, no error — the
issue is created with the label missing, and intake quietly stops being
filterable. Create all three before enabling the issue templates.

## 4. Verify

```bash
bash run-tests.sh
```

Must be green (12 passed, 0 failed) before the first push.

Then, on a **copy**, confirm the safety gate still refuses to run an unsafe
measurer:

```bash
T=$(mktemp -d); cp -r . "$T"/
printf '\nomarchy theme set nord\n' >> "$T"/tools/measure.py
(cd "$T" && bash run-tests.sh)   # must FAIL at step 0
rm -rf "$T"
```

## What must not be committed

- Anything from `~/.config`, `~/Projects`, or a shell history.
- Machine-identifying data. `run-tests.sh` step 4 fails on `/home/<name>` and
  `/root` paths in `baseline/`, which is why that gate exists — the baseline
  goes public.
- PIDs. `measure.py` aggregates per program name precisely so a committed
  baseline stays reproducible on someone else's machine.

## What a PR must not contain

No patch to the installed system. No change outside this repository. The PR
template states it, and it means it: no edits under `/usr/bin`,
`/usr/share/omarchy`, or `~/.config/omarchy`, no theme changes, no shell
restart, and no `omarchy` subcommand that writes.

This repository documents; it does not act. Acting on a record is a patch to
Omarchy, and that belongs somewhere else.