---
id: KB-012-install-footprint-wallpapers
title: 97% of the install is wallpapers, and they decode to 4.5 GB
type: measurement
status: accepted
strength: strong
surface: themes, config
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

The install is **121.7 MB**. Themes are **118.3 MB** of it — **97%**.

Within themes, `*/backgrounds/` holds **92** image files totalling **107.1 MB**
on disk. Decoded at 4 bytes per pixel, which is what a compositor does with
them, they occupy **4,488.9 MB**.

The largest, `tokyo-night/backgrounds/0-winding-road.jpg`, is **6016×3384** —
about **81 MB** decoded, from 4.4 MB of JPEG. **29 of the 92** exceed 64 MB
decoded.

For scale: this machine runs two displays, the largest **1920×1080**. The
largest wallpaper is oversampled by more than 3× on each axis. The 2560-wide
suggestion in [KB-020](../KB-020-wallpaper-resolution.md) would still be a
downscale on this hardware.

Duplicated content is negligible — only 2 of the 158 image files across all
themes are byte-identical. This is not a packaging mistake; it is the intended
design.

## Proposal

**Measure and publish the footprint — which is what this record is.**

The reduction is [KB-020](../KB-020-wallpaper-resolution.md). Keeping them
separate matters: this record is the fact, that one is the argument, and the
argument depends on a fact a reader can check.

### The one claim nobody can verify from here

> "No visible difference at 2560 wide."

**That is an appearance claim, and this repository cannot check it.** By the
rule this project is built under, an agent cannot verify how something looks on
a screen. The measurement above is solid — decoded dimensions come from image
headers, not from estimation. The *harmlessness* of downscaling is asserted,
not verified, and a human has to look at it before anyone acts on KB-020.

This is flagged here as well as in KB-020 because this is the record that
supplies the numbers, and a reader who stops here should see the limit.

## Pros

- The single largest measured fact in the system, and it is unambiguous.
- Every reader can reproduce it in one command, and every reader's number will
  be close to theirs — this is not machine-specific.
- Separating fact from proposal lets someone accept the measurement and reject
  the reduction, which is a legitimate position.

## Cons

- **Decoded size is a modelling choice.** 4 bytes per pixel is what a
  compositor allocates for an XRGB surface. A compositor that downsamples
  before allocating, or uses a compressed texture, decodes far less. The 4.5 GB
  is an upper bound on the decode cost, not a measurement of it. Nobody has
  measured Quickshell's actual allocation for a full-screen image.
- **RAM is not obviously the constraint.** The wallpapers are decoded on demand
  — only the current background is live. So the 4.5 GB is not resident memory,
  and quoting it as though it were would be wrong. The real cost is disk, the
  package, and decode time at login.
- **Resolution may be deliberate.** Wallpapers ship at high resolution so they
  look right on a 4K or 5K display, on a TV, or after a future panel upgrade.
  That is a defensible product decision, not an oversight.
- The figure says nothing about whether users notice, which is the only thing
  that matters for whether it should change.

## Risk

**Low as a measurement; the risk is misquoting it.**

Two ways to get this wrong, both easy:

1. Quoting 4.5 GB as memory use. It is not — the decode is transient.
2. Quoting it as a defect. It may be an intentional quality choice.

The record states both limits so that a reader who quotes it has to quote the
caveat too.

## Evidence

```bash
# the footprint, from the measurement tooling
bash tools/measure.sh
python3 -c "
import json; d=json.load(open('baseline/measurements.json'))['footprint']
print('install MB  ', round(d['installBytes']/1048576, 1))
print('themes MB   ', round(d['themesBytes']/1048576, 1))
print('theme share ', d['themeShareOfInstall'])
print('wallpapers  ', d['wallpaperCount'], 'files,',
      round(d['wallpaperStoredBytes']/1048576, 1), 'MB stored')
print('decoded GB  ', round(d['wallpaperDecodedBytes']/1073741824, 2))
print('over 64MB   ', len(d['oversizedWallpapers']))"

# the largest, with real dimensions from the header
identify /usr/share/omarchy/themes/tokyo-night/backgrounds/0-winding-road.jpg

# and what the display actually needs
hyprctl monitors | grep -E 'resolution|active'
```

To check the claim this repository cannot: resize one image and look at it.

```bash
magick /usr/share/omarchy/themes/tokyo-night/backgrounds/0-winding-road.jpg \
      -resize 2560x /tmp/2560.jpg
# then view /tmp/2560.jpg full-screen. that step is a human's.
```

## Amendment history

- 2026-09-30 — initial record.