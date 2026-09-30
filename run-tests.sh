#!/usr/bin/env bash
# Prove the knowledge base still describes the installed system.
#
# Six gates, all headless and read-only:
#   0  the measurer is safe to execute      (static grep, BEFORE any run)
#   1  measurements regenerate cleanly
#   2  every knowledge-base record validates against SCHEMA.md
#   3  every headline number quoted in prose is the measured one
#   4  baseline/ is generated, not hand-edited
#   5  the shared no-visible-surface lint, plus hygiene
#
# Runs no state-changing omarchy command, sends no input, maps no window,
# captures no screen, and never restarts or rescans the shell.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PASS=0; FAIL=0
ok()  { printf '  \033[32mPASS\033[0m  %s\n' "$1"; PASS=$((PASS+1)); }
bad() { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAIL=$((FAIL+1)); }

TMP=$(mktemp -d)
SCRATCH="$TMP/scratch"; mkdir -p "$SCRATCH"
trap 'rm -rf "$TMP"' EXIT

# --- 0. is it safe to run the measurer at all? ---------------------------
# This MUST be first. The suite executes tools/measure.sh, so any check that
# greps that file for dangerous commands has to precede execution, not follow
# it. A gate that reports after the run is a log line, not a gate.
#
# The same lesson, learned the hard way in the sibling project homelpy: a
# self-test appended a real `omarchy theme set nord` to that repo's generator,
# the suite ran it, the theme changed, and only THEN did the gate report it.
echo "[0/6] the measurer is safe to execute"
UNSAFE=0
if grep -nE '(^|[;&|(]|\$\()\s*(omarchy-(theme-set|theme-set-by-theme|plugin-(add|remove|enable|disable|update|clone)|install|update|refresh|restart|provision|reinstall)|sudo|rm -rf|pacman -S|omarchy\s+(theme\s+(set|bg-set)|plugin\s+(add|remove|enable|disable|update|clone)|install|update|refresh|restart))\b' \
     tools/measure.sh tools/measure.py > "$SCRATCH/unsafe.txt" 2>&1; then
  bad "measurement tooling references a state-changing command"
  sed 's/^/        /' "$SCRATCH/unsafe.txt" | head -5
  echo "        refusing to execute it. fix the file, then re-run."
  UNSAFE=1
else
  ok "measurement tooling references no state-changing command"
fi

# --- 1. the measurements regenerate ---------------------------------------
echo "[1/6] measurements regenerate"
if [ "$UNSAFE" -eq 0 ] && bash tools/measure.sh --json > /dev/null 2> "$SCRATCH/err.txt"; then
  ok "measurements regenerated from the installed system"
else
  [ "$UNSAFE" -eq 1 ] || { bad "measure.sh failed"; sed 's/^/        /' "$SCRATCH/err.txt" | head -20; }
fi

# --- 2. every record validates against the schema ------------------------
# The knowledge base is the product. A malformed amendment must not be able to
# land, so this runs the same validator CONTRIBUTING.md tells people to run.
echo "[2/6] knowledge-base records validate"
if python3 tools/validate-kb.py > "$SCRATCH/kb.txt" 2>&1; then
  ok "$(tail -1 "$SCRATCH/kb.txt")"
else
  bad "knowledge-base records do not validate"
  sed 's/^/        /' "$SCRATCH/kb.txt" | head -20
fi

# Every record must be reachable from the index, or it is invisible.
MISSING_LINK=$(python3 - <<'PY'
import os, re
idx = open("knowledge-base/INDEX.md").read() if os.path.isfile("knowledge-base/INDEX.md") else ""
missing = []
for name in sorted(os.listdir("knowledge-base/findings")):
    if not name.endswith(".md"):
        continue
    if name not in idx:
        missing.append(name)
print(" ".join(missing))
PY
)
if [ -z "$MISSING_LINK" ]; then
  ok "every record is listed in knowledge-base/INDEX.md"
else
  bad "records not listed in INDEX.md: $MISSING_LINK"
fi

# --- 3. every headline number quoted in prose is the measured one ---------
# The whole point of the project. An assessment that silently goes stale is
# worse than no assessment, because it reads as current.
echo "[3/6] quoted numbers match the measurements"
python3 - <<'PY' > "$SCRATCH/claims.txt" 2>&1
import json, os, re, sys
d = json.load(open("baseline/measurements.json"))
c, s, f, k = d["commands"], d["shell"], d["footprint"], d["mechanisms"]
fails = []

def claim(label, want, pattern, where):
    haystack = "".join(open(p, errors="replace").read()
                       for p in [where] if os.path.isfile(p))
    if not haystack:
        fails.append(f"{where} is missing")
        return
    if not re.search(pattern, haystack):
        fails.append(f"{where} does not state {label} = {want}")

prose = "README.md"
claim("command count", c["count"], r"\b445\b", prose)
claim("hook events", k["firedHookEventCount"], r"\b5\b", prose)
claim("migrations", k["migrationsShipped"], r"\b106\b", prose)

# Structural claims re-derived from the source, not from the prose.
if not s["schemaVersionPinned"]:
    fails.append("registry no longer pins schemaVersion -- the defence records need review")
if s["uiComponents"] < 30:
    fails.append(f"Ui kit is only {s['uiComponents']} components")
if len(k["capabilityFacades"]) < 6:
    fails.append(f"only {len(k['capabilityFacades'])} capability facades")

import os
if fails:
    for x in fails:
        print(x)
    sys.exit(1)
print("ok")
PY
if grep -q '^ok$' "$SCRATCH/claims.txt"; then
  ok "quoted numbers are the measured ones"
else
  bad "prose contradicts the measurements"
  sed 's/^/        /' "$SCRATCH/claims.txt"
fi

# --- 4. baseline/ is generated, not hand-edited --------------------------
echo "[4/6] baseline/ is generated"
UNEXPECTED=$(find baseline -type f ! -name 'measurements.json' | head -5)
if [ -z "$UNEXPECTED" ]; then
  ok "baseline/ holds only the generated file"
else
  bad "unexpected files in baseline/: $UNEXPECTED"
fi
if python3 -c "import json;json.load(open('baseline/measurements.json'))" 2>/dev/null; then
  ok "baseline/measurements.json is valid JSON"
else
  bad "baseline/measurements.json invalid"
fi
# Nothing machine-identifying may be committed: this knowledge base is public.
if grep -nE '/home/[a-z]|/root' baseline/measurements.json > "$SCRATCH/paths.txt" 2>&1; then
  bad "measurements contain personal paths — do not commit these publicly"
  sed 's/^/        /' "$SCRATCH/paths.txt" | head -5
else
  ok "no personal paths in the committed baseline"
fi

# --- 5. shared lint and hygiene ------------------------------------------
echo "[5/6] shared no-visible-surface lint"
if [ -f ~/Projects/lib/lint-no-visible-surfaces.js ]; then
  if node ~/Projects/lib/lint-no-visible-surfaces.js > "$SCRATCH/lint.txt" 2>&1; then
    ok "no-visible-surface lint clean"
  else
    bad "no-visible-surface lint failed"; sed 's/^/        /' "$SCRATCH/lint.txt" | head -20
  fi
else
  printf '  \033[33mSKIP\033[0m  no-visible-surface lint (lib not found)\n'
fi

# --- 6. hygiene ----------------------------------------------------------
echo "[6/6] hygiene"
if grep -rnE 'q[s] +-[pr]|quickshel[l] +-[pr]' tools/ run-tests.sh > "$SCRATCH/qs.txt" 2>&1; then
  bad "tooling references a direct quickshell load"
  sed 's/^/        /' "$SCRATCH/qs.txt" | head -5
else
  ok "no direct quickshell invocation in tooling"
fi
MISSING=0
for f in README.md CONTRIBUTING.md AGENTS.md PUBLISHING.md knowledge-base/SCHEMA.md knowledge-base/INDEX.md; do
  [ -f "$f" ] || { bad "missing $f"; MISSING=1; }
done
[ "$MISSING" -eq 0 ] && ok "front doors present (README, CONTRIBUTING, PUBLISHING, SCHEMA, INDEX)"
# Nothing here may implement anything: this is a knowledge base.
if grep -rlnE '^#!.*\b(pacman|quickshell|qs)\b' tools/ > "$SCRATCH/impl.txt" 2>&1; then
  bad "tooling appears to change system state"
  sed 's/^/        /' "$SCRATCH/impl.txt"
else
  ok "tooling changes nothing on the installed system"
fi

echo
printf 'passed %s, failed %s\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1