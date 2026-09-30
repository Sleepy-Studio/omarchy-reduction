#!/usr/bin/env python3
"""Measure Omarchy's surface, size and runtime footprint.

Everything written to baseline/measurements.json is read from the installed
system or the shipped source. Nothing is hand-authored, so run-tests.sh can
prove the assessment still describes reality.

Read-only: runs no state-changing omarchy command, sends no input, maps no
window, captures no screen, never restarts or rescans the shell.
"""

import argparse
import glob
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time

APPROX_KB = 1024


# ---------------------------------------------------------------- helpers

def lines(path):
    with open(path, errors="replace") as fh:
        return sum(1 for _ in fh)


def dir_bytes(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total


def image_dims(path):
    """Width/height from JPEG or PNG headers, without decoding pixels."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(65536)
    except OSError:
        return None
    if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
        w, h = struct.unpack(">II", head[16:24])
        return w, h
    if head[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(head) - 9:
        if head[i] != 0xFF:
            i += 1
            continue
        marker = head[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", head[i + 5:i + 9])
            return w, h
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg = struct.unpack(">H", head[i + 2:i + 4])[0]
        i += 2 + seg
    return None


def timeit(argv, runs=5):
    for _ in range(2):                      # warm the page cache
        subprocess.run(argv, capture_output=True)
    t0 = time.monotonic()
    for _ in range(runs):
        subprocess.run(argv, capture_output=True)
    return round((time.monotonic() - t0) / runs * 1000, 1)


# ------------------------------------------------------- command surface

def measure_commands(bindir):
    files = [p for p in sorted(glob.glob(os.path.join(bindir, "omarchy*")))
             if os.path.isfile(p) and not os.path.islink(p)]

    buckets = {"thin_le15": 0, "mid_16_60": 0, "mid_61_300": 0, "large_gt300": 0}
    total_lines = 0
    meta = {"summary": 0, "name": 0, "args": 0, "examples": 0,
            "requiresSudo": 0, "hidden": 0, "aliases": 0}
    groups, families = set(), {}
    head_re = re.compile(r"^#\s*omarchy:([a-zA-Z_-]+)=")
    shim_via = 0

    for path in files:
        n = lines(path)
        total_lines += n
        if n <= 15:
            buckets["thin_le15"] += 1
        elif n <= 60:
            buckets["mid_16_60"] += 1
        elif n <= 300:
            buckets["mid_61_300"] += 1
        else:
            buckets["large_gt300"] += 1

        name = os.path.basename(path)[len("omarchy-"):]
        family = "-".join(name.split("-")[:2])
        families[family] = families.get(family, 0) + 1

        declared = False
        with open(path, errors="replace") as fh:
            body = fh.read()
        for line in body.splitlines():
            # The metadata header is the leading run of shebang/blank/comment
            # lines. A blank line after the shebang must not end it, or every
            # command reads as undeclared.
            if line.startswith("#!") or not line.strip():
                continue
            if not line.startswith("#"):
                break
            mm = head_re.match(line)
            if not mm:
                continue
            declared = True
            key = mm.group(1)
            value = line.split("=", 1)[1].strip()
            if key == "group":
                groups.add(value)
            elif key == "hidden" and value == "true":
                meta["hidden"] += 1
            elif key == "requires-sudo" and value == "true":
                meta["requiresSudo"] += 1
            elif key in ("alias", "aliases"):
                meta["aliases"] += 1
            elif key in meta:
                meta[key] += 1
        if not declared:
            shim_via += 1

    largest = sorted(((lines(p), os.path.basename(p)[len("omarchy-"):])
                      for p in files), reverse=True)[:10]
    dupes = duplicate_bodies(files)

    return {
        "count": len(files),
        "linesTotal": total_lines,
        "sizeBuckets": buckets,
        "metadata": meta,
        "groupCount": len(groups),
        "undeclaredMetadata": shim_via,
        "largest": largest,
        "largestFamilies": sorted(families.items(), key=lambda kv: -kv[1])[:12],
        "duplicateBodies": dupes,
        "dispatcherMs": {
            "version": timeit([os.path.join(bindir, "omarchy"), "version"]),
            "themeList": timeit([os.path.join(bindir, "omarchy"), "theme", "list"]),
        } if os.path.exists(os.path.join(bindir, "omarchy")) else {},
    }


def duplicate_bodies(files):
    by_hash = {}
    for path in files:
        with open(path, "rb") as fh:
            data = fh.read()
        if len(data) > 2000:
            continue
        by_hash.setdefault(hashlib.md5(data).hexdigest(), []).append(
            os.path.basename(path)[len("omarchy-"):])
    return sorted([sorted(v) for v in by_hash.values() if len(v) > 1])


# ------------------------------------------------------------------ shell

def measure_shell(omarchy_path):
    shell = os.path.join(omarchy_path, "shell")
    qml = sorted(glob.glob(os.path.join(shell, "**", "*.qml"), recursive=True))
    js = sorted(glob.glob(os.path.join(shell, "**", "*.js"), recursive=True))

    panel_models = sorted(glob.glob(os.path.join(shell, "plugins", "panels", "*", "Model.js")))
    ui = os.path.join(shell, "Ui")
    commons = os.path.join(shell, "Commons")

    registry = os.path.join(shell, "services", "PluginRegistry.qml")
    src = open(registry, errors="replace").read() if os.path.isfile(registry) else ""

    return {
        "qmlFiles": len(qml),
        "qmlLines": sum(lines(p) for p in qml),
        "jsFiles": count_files(js),
        "jsLines": sum(lines(p) for p in js),
        "shellRootLines": lines(os.path.join(shell, "shell.qml")),
        "uiComponents": count_files(glob.glob(os.path.join(ui, "*.qml"))),
        "commonsSingletons": count_files(glob.glob(os.path.join(commons, "*.qml"))),
        "panelCount": len(panel_models),
        "panelModelLines": sum(lines(p) for p in panel_models),
        "oversized": sorted(((lines(p), os.path.relpath(p, shell)) for p in qml),
                            reverse=True)[:10],
        "schemaVersionPinned": "schemaVersion" in src,
        "registryLines": lines(registry) if os.path.isfile(registry) else 0,
    }


def count_files(paths):
    return len([p for p in paths if os.path.isfile(p)])


# -------------------------------------------------------------- footprint

def measure_footprint(omarchy_path):
    themes = os.path.join(omarchy_path, "themes")
    wallpapers, wallpaper_bytes = 0, 0
    decoded = []
    hashes = {}
    for path in glob.glob(os.path.join(themes, "**", "*.*"), recursive=True):
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as fh:
            digest = hashlib.md5(fh.read()).hexdigest()
        hashes.setdefault(digest, []).append(os.path.relpath(path, omarchy_path))
        if os.sep + "backgrounds" + os.sep not in path:
            continue
        if os.path.splitext(path)[1].lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        wallpapers += 1
        size = os.path.getsize(path)
        wallpaper_bytes += size
        dims = image_dims(path)
        if dims:
            w, h = dims
            decoded.append({
                "file": os.path.relpath(path, omarchy_path),
                "width": w, "height": h,
                "decodedBytes": w * h * 4,          # decoded RGBA8888
                "storedBytes": size,
            })

    decoded.sort(key=lambda d: -d["decodedBytes"])
    install = dir_bytes(omarchy_path)
    theme_bytes = dir_bytes(themes)
    dupes = [sorted(v) for v in hashes.values() if len(v) > 1]

    return {
        "installBytes": install,
        "themesBytes": theme_bytes,
        "themeShareOfInstall": round(theme_bytes / max(1, install), 3),
        "wallpaperCount": wallpapers,
        "wallpaperStoredBytes": wallpaper_bytes,
        "wallpaperDecodedBytes": sum(d["decodedBytes"] for d in decoded),
        "oversizedWallpapers": [d for d in decoded if d["decodedBytes"] > 64 * 1024 * 1024],
        "largestWallpapers": decoded[:8],
        "duplicateFiles": dupes,
        "configTemplateDirs": sorted(os.listdir(os.path.join(omarchy_path, "config"))),
        "defaultTreeDirs": sorted(os.listdir(os.path.join(omarchy_path, "default"))),
    }


# --------------------------------------------------------------- runtime

def measure_runtime():
    procs = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            comm = open(f"/proc/{pid}/comm").read().strip()
            if "quickshell" not in comm and not comm.startswith("omarchy"):
                continue
            rollup = open(f"/proc/{pid}/smaps_rollup").read()
        except Exception:
            continue
        anon = re.search(r"^Anonymous:\s+(\d+) kB", rollup, re.M)
        dirty = re.search(r"^Private_Dirty:\s+(\d+) kB", rollup, re.M)
        huge = re.search(r"^AnonHugePages:\s+(\d+) kB", rollup, re.M)
        procs.append({
            "pid": int(pid), "comm": comm,
            "anonymousKb": int(anon.group(1)) if anon else 0,
            "privateDirtyKb": int(dirty.group(1)) if dirty else 0,
            "anonHugePagesKb": int(huge.group(1)) if huge else 0,
        })
    # One aggregate row per program, never per PID. A PID is ephemeral and
    # machine-specific, so recording it makes the committed baseline
    # unreproducible on anyone else's box and leaks nothing useful.
    by_comm = {}
    for p in procs:
        agg = by_comm.setdefault(p["comm"], {"instances": 0, "anonymousKb": 0,
                                             "privateDirtyKb": 0})
        agg["instances"] += 1
        agg["anonymousKb"] += p["anonymousKb"]
        agg["privateDirtyKb"] += p["privateDirtyKb"]
    rows = [{"program": comm, **vals} for comm, vals in by_comm.items()]
    rows.sort(key=lambda r: -r["anonymousKb"])

    return {
        "programs": rows,
        "quickshellAnonymousKb": next(
            (r["anonymousKb"] for r in rows if r["program"] == "quickshell"), 0),
        "totalAnonymousKb": sum(p["anonymousKb"] for p in procs),
        "systemProcessCount": len([p for p in os.listdir("/proc") if p.isdigit()]),
    }


# ---------------------------------------------------------- extensibility

def measure_mechanisms(omarchy_path):
    shell = os.path.join(omarchy_path, "shell")
    services = os.path.join(shell, "services")

    fired = {}
    bindir = os.path.join(omarchy_path, "bin")
    for path in sorted(glob.glob(os.path.join(bindir, "*"))):
        if not os.path.isfile(path):
            continue
        src = open(path, errors="replace").read()
        for mm in re.finditer(r"omarchy-hook(?:-install)?\s+([a-z0-9][a-z0-9-]*)", src):
            if mm.group(1) == "install":
                continue
            fired.setdefault(mm.group(1), []).append(os.path.basename(path))

    themed = os.path.join(omarchy_path, "default", "themed")
    hypr = os.path.join(omarchy_path, "default", "hypr", "bindings")

    return {
        "firedHookEvents": dict(sorted(fired.items())),
        "firedHookEventCount": len(fired),
        "migrationsShipped": count_files(glob.glob(os.path.join(omarchy_path, "migrations", "*.sh"))),
        "themedTemplates": sorted(os.listdir(themed)) if os.path.isdir(themed) else [],
        "capabilityFacades": sorted(os.path.basename(p) for p in
                                    glob.glob(os.path.join(services, "*Api.qml"))),
        "hostServices": sorted(os.path.basename(p) for p in
                               glob.glob(os.path.join(services, "*.qml"))),
        "hyprBindingModules": sorted(os.path.relpath(p, os.path.dirname(hypr))
                                     for p in glob.glob(os.path.join(hypr, "**", "*.lua"),
                                                        recursive=True)),
    }


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omarchy-bin", default="/usr/bin")
    ap.add_argument("--omarchy-path", default="/usr/share/omarchy")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(os.path.join(args.omarchy_path, "shell")):
        sys.exit(f"measure: no shell source at {args.omarchy_path}/shell")

    data = {
        "generatedBy": "tools/measure.sh",
        "measuredOn": time.strftime("%Y-%m-%d"),
        "commands": measure_commands(args.omarchy_bin),
        "shell": measure_shell(args.omarchy_path),
        "footprint": measure_footprint(args.omarchy_path),
        "runtime": measure_runtime(),
        "mechanisms": measure_mechanisms(args.omarchy_path),
    }

    with open(args.out, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        human(data)


def mb(n):
    return f"{n / (1024 * 1024):.1f} MB"


def human(d):
    c, s, f, r, k = d["commands"], d["shell"], d["footprint"], d["runtime"], d["mechanisms"]
    print(f"commands        {c['count']}  ({c['linesTotal']} lines of bash)")
    b = c["sizeBuckets"]
    print(f"  by size       {b['thin_le15']} <=15 lines, {b['mid_16_60']} 16-60, "
          f"{b['mid_61_300']} 61-300, {b['large_gt300']} >300")
    print(f"  undeclared    {c['undeclaredMetadata']} commands carry no omarchy: metadata")
    print(f"  dispatcher    {c['dispatcherMs'].get('version')} ms per invocation "
          f"(re-scans every omarchy-* header)")
    print(f"shell           {s['qmlLines']} lines QML across {s['qmlFiles']} files, "
          f"{s['jsLines']} lines JS")
    print(f"  panel models  {s['panelModelLines']} lines across {s['panelCount']} panels "
          f"(no shared data layer)")
    print(f"install         {mb(f['installBytes'])}, of which themes "
          f"{mb(f['themesBytes'])} ({f['themeShareOfInstall'] * 100:.0f}%)")
    print(f"  wallpapers    {f['wallpaperCount']} files, {mb(f['wallpaperStoredBytes'])} on disk, "
          f"{mb(f['wallpaperDecodedBytes'])} decoded at 4bpp")
    print(f"  oversized     {len(f['oversizedWallpapers'])} decode to >64 MB each")
    print(f"runtime         quickshell anon {r['quickshellAnonymousKb']} kB, "
          f"total omarchy anon {r['totalAnonymousKb']} kB, "
          f"{r['systemProcessCount']} processes on the box")
    print(f"extensibility   {k['firedHookEventCount']} hook events, "
          f"{k['migrationsShipped']} migrations, {len(k['themedTemplates'])} themed templates, "
          f"{len(k['capabilityFacades'])} capability facades")


if __name__ == "__main__":
    main()