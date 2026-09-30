---
id: KB-020-wallpaper-resolution
title: Ship wallpapers at display resolution, not source resolution
type: reduction
status: proposed
strength: strong
surface: themes, config
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

Wallpapers are 97% of the install and an order of magnitude larger than
anything else in it.

The measured facts (`baseline/measurements.json` → `footprint`):

- `/usr/share/omarchy` is **121.7 MB**; `themes/` is **118.3 MB**, so **97%**.
- Of that, **92** files in `*/backgrounds/` account for **107.1 MB** on disk.
- Decoded at 4 bytes per pixel — what a compositor actually does with them —
  they occupy **4,488.9 MB**.
- The largest, `tokyo-night/backgrounds/0-winding-road.jpg`, is **6016×3384**:
  about **81 MB** decoded.
- **29 of the 92** exceed 64 MB decoded.

The machine this was measured on runs two displays, the largest 1920×1080.
Every one of these images is oversampled by at least 4× on each axis, and the
biggest by more than 9×.

This is not a style complaint. It is the largest single avoidable cost in the
installed system, and it is paid on disk at install, in the package, and in
decoder memory at every login.

## Proposal

Generate the wallpapers at the display's resolution at install time, or ship
them capped at **2560 px wide** and let the compositor upscale.

Concretely, two acceptable shapes:

1. **Ship-time.** A packaging step downsamples each background to a maximum
   dimension. Zero runtime cost, one fewer thing to go wrong.
2. **Install-time.** A script renders the backgrounds at the connected
   display's actual resolution, per machine.

Ship-time is simpler and more predictable. Install-time adapts to a 4K panel
but adds a step that can be interrupted and a cache that can go stale.

**Keep one full-resolution original per theme** if the goal is to preserve
headroom. That costs 22 files instead of 92 and still removes the bulk.

### Why 2560

It is roughly 1/6 the pixel count of 6016 wide and covers a 2560×1440 panel
natively. On a 1920×1080 display it remains a slight downscale, so it is not
the conservative choice at the low end — a 1920 cap would be, at the cost of
losing 1440p-class displays.

## Pros

- The single largest reduction available: ~107 MB of the 121.7 MB install is
  wallpapers, and the decoded footprint drops from 4.5 GB by roughly an order
  of magnitude.
- No behavioural change. Nothing in the system depends on wallpaper
  resolution; they are decoded and scaled.
- It reduces the *package*, so it helps everyone, not just this install.
- It is the one item here with essentially no downside.

## Cons

- **It is an appearance change and nobody has checked it.** "No visible
  difference on this hardware" is a claim about a screen, and by this
  project's own rule an agent cannot verify appearance. This is the honest
  limit of the record: the reduction is measured, the *harmlessness* is
  asserted.
- Upscaling artefacts are real on a 4K panel if the cap is too low. 2560 is a
  judgement, not a derivation.
- Install-time rendering adds a failure mode at install, which is the worst
  possible time for one.
- If someone later ships a 5K or 8K display, a hard 2560 cap becomes a
  downgrade rather than a saving.

## Risk

**Low, and loud if wrong.**

Nothing breaks: a lower-resolution wallpaper renders. The failure mode is
"it looks worse", which is immediately obvious to a human and invisible to
every automated gate here — which is precisely why it must be checked by a
person before it is acted on.

The real risk is shipping it *without* that check and calling the result
verified.

## Evidence

Anyone can reproduce the measurement:

```bash
bash tools/measure.sh          # the footprint block
python3 -c "
import json; d=json.load(open('baseline/measurements.json'))['footprint']
print(d['wallpaperCount'], d['wallpaperStoredBytes'], d['wallpaperDecodedBytes'])
print(len(d['oversizedWallpapers']), 'exceed 64 MB decoded')
print(*d['largestWallpapers'][:5], sep='\n')"
```

And check what a display actually needs:

```bash
hyprctl monitors | grep -E 'resolution|active'
```

To compare before committing to a cap, resize one image and look at it side
by side:

```bash
magick tokyyo-night/backgrounds/0-winding-road.jpg -resize 2560x /tmp/2560.jpg
magick tokyyo-night/backgrounds/0-winding-road.jpg -resize 1920x /tmp/1920.jpg
# then look at all three. this is the step an agent cannot do.
```

## Amendment history

- 2026-09-30 — initial record.