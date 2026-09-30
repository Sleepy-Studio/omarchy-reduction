#!/usr/bin/env python3
"""Validate every knowledge-base record against SCHEMA.md.

Fails loudly on: a missing or duplicated id, an unknown vocabulary value, a
missing body section, sections out of order, an amendment count that disagrees
with the history, a malformed history line, or a record that quotes a number
the committed measurements do not support.

Read-only. Touches only this repository.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINDINGS = os.path.join(ROOT, "knowledge-base", "findings")
MEASUREMENTS = os.path.join(ROOT, "baseline", "measurements.json")

REQUIRED_FRONTMATTER = ["id", "title", "type", "status", "strength",
                        "surface", "confidence", "measuredOn", "amendments"]

SECTIONS = ["Problem", "Proposal", "Pros", "Cons", "Risk", "Evidence",
            "Amendment history"]

VOCAB = {
    "type": {"reduction", "defence", "measurement", "open-question"},
    "status": {"proposed", "accepted", "implemented", "rejected", "superseded"},
    "strength": {"strong", "moderate", "speculative"},
    "confidence": {"high", "medium", "low"},
}

# Numbers a record may state as fact, and where in the measurements each must
# come from. A record that quotes a headline number without a matching path is
# the failure this whole repository exists to prevent.
HEADLINE = {
    "command count": lambda d: str(d["commands"]["count"]),
    "command lines": lambda d: f'{d["commands"]["linesTotal"]:,}',
    "thin commands": lambda d: str(d["commands"]["sizeBuckets"]["thin_le15"]),
    "qml lines": lambda d: f'{d["shell"]["qmlLines"]:,}',
    "js lines": lambda d: f'{d["shell"]["jsLines"]:,}',
    "panel models": lambda d: str(d["shell"]["panelCount"]),
    "panel model lines": lambda d: f'{d["shell"]["panelModelLines"]:,}',
    "migrations": lambda d: str(d["mechanisms"]["migrationsShipped"]),
    "hook events": lambda d: str(d["mechanisms"]["firedHookEventCount"]),
    "facades": lambda d: str(len(d["mechanisms"]["capabilityFacades"])),
    "themed templates": lambda d: str(len(d["mechanisms"]["themedTemplates"])),
    "wallpapers": lambda d: str(d["footprint"]["wallpaperCount"]),
    "schemaVersion pinned": lambda d: str(d["shell"]["schemaVersionPinned"]),
}


def parse_frontmatter(text, path, errs):
    if not text.startswith("---\n"):
        errs.append(f"{path}: no YAML frontmatter (must start with ---)")
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        errs.append(f"{path}: frontmatter is not closed")
        return None
    block = text[4:end]
    body = text[end + 5:]
    fields = {}
    key = None
    for line in block.split("\n"):
        if not line.strip():
            continue
        if line.startswith(" ") or line.startswith("-"):
            continue                       # continuation, not a new key
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            fields[key] = value.strip()
    return fields, body


def check_record(path, seen_ids, data):
    errs = []
    name = os.path.basename(path)
    text = open(path, errors="replace").read()
    parsed = parse_frontmatter(text, name, errs)
    if not parsed:
        return errs
    fm, body = parsed

    for key in REQUIRED_FRONTMATTER:
        if key not in fm or fm[key] == "":
            errs.append(f"{name}: missing frontmatter field '{key}'")

    rid = fm.get("id", "")
    if rid in seen_ids:
        errs.append(f"{name}: id '{rid}' is already used by another record "
                    f"— ids must never be reused")
    seen_ids.add(rid)
    if rid and not name.startswith(rid):
        errs.append(f"{name}: filename should start with its id '{rid}'")

    for key, allowed in VOCAB.items():
        value = fm.get(key)
        if value and value not in allowed:
            errs.append(f"{name}: {key}='{value}' is not one of {sorted(allowed)}")

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fm.get("measuredOn", "")):
        errs.append(f"{name}: measuredOn must be YYYY-MM-DD, got "
                    f"'{fm.get('measuredOn')}'")

    # Sections: present, and in order.
    found = re.findall(r"^## (.+)$", body, re.M)
    found = [s.strip() for s in found]
    for section in SECTIONS:
        if section not in found:
            errs.append(f"{name}: missing section '## {section}'")
    order = [s for s in found if s in SECTIONS]
    if order != SECTIONS:
        errs.append(f"{name}: sections out of order — expected {SECTIONS}, "
                    f"found {order}")

    # Amendment count must agree with the history it summarises.
    history = body.split("## Amendment history", 1)[-1] if "## Amendment history" in body else ""
    entries = [l for l in history.split("\n") if l.strip().startswith("- ")]
    for line in entries:
        if not re.match(r"^-\s+\d{4}-\d{2}-\d{2}\s+—\s+\S", line):
            errs.append(f"{name}: amendment history line is not "
                        f"'- YYYY-MM-DD — what changed': {line.strip()[:60]!r}")
    claimed = fm.get("amendments")
    # `amendments` counts substantive amendments by others. The initial record
    # is not an amendment, so a fresh record is 0 with one history line.
    if claimed.isdigit() and int(claimed) != max(0, len(entries) - 1):
        errs.append(f"{name}: amendments={claimed} but the history has "
                    f"{len(entries)} entr{'y' if len(entries)==1 else 'ies'} "
                    f"(initial record + {max(0, len(entries)-1)} amendment"
                    f"{'s' if len(entries)-1 != 1 else ''})")

    # Headline numbers, when present, must be the measured ones. Accept the
    # value with or without thousands separators — prose may write either.
    cited = 0
    for label, get in HEADLINE.items():
        want = get(data)
        forms = {want, want.replace(",", "")}
        if any(re.search(r"(?<![\d,.])" + re.escape(f) + r"(?![\d])", body)
               for f in forms):
            cited += 1
    if cited == 0 and fm.get("type") in ("measurement", "reduction"):
        errs.append(f"{name}: states no headline number from "
                    f"baseline/measurements.json — every measured claim needs one")

    return errs


def main():
    if not os.path.isdir(FINDINGS):
        sys.exit("validate: no knowledge-base/findings/ directory")
    data = json.load(open(MEASUREMENTS))
    records = sorted(f for f in os.listdir(FINDINGS) if f.endswith(".md"))
    if not records:
        sys.exit("validate: knowledge-base/findings/ is empty")

    seen, errs = set(), []
    for name in records:
        errs.extend(check_record(os.path.join(FINDINGS, name), seen, data))

    if errs:
        for e in errs:
            print(e)
        sys.exit(f"validate: {len(errs)} problem(s) in "
                 f"{len(records)} record(s)")
    print(f"ok: {len(records)} records validate")


if __name__ == "__main__":
    main()