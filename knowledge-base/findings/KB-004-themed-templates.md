---
id: KB-004-themed-templates
title: One palette rendered into 19 app configs is the system's best abstraction
type: defence
status: accepted
strength: strong
surface: themes, config
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

A theme is a directory of per-application config fragments — `alacritty.toml`,
`foot.ini`, `ghostty.conf`, `btop.theme`, `hyprland.lua`, and a dozen more —
that have to agree on colour. With 22 themes and 19 themed applications, that
is a lot of files that must stay in sync, and nothing structurally forces them
to.

The obvious reduction is to drop the per-app files and let each application
read the palette itself. That would delete 19 files per theme, and it would
mean 19 independent implementations of "read this palette", each with its own
format quirks, its own colour-space handling, and its own bugs.

## Proposal

**Keep the template layer, and treat it as the model rather than the oddity.**

What `omarchy-theme-set-templates` (~404 lines) does: takes one
`colors.toml` palette, and `sed`-renders 19 `.tpl` files into every app's real
config. The shell is the same abstraction at a different layer — one
`PluginRegistryApi` per capability, one `CachedPoll` per data source — and the
templates are the one place it is applied completely.

If a new reduction in this knowledge base is hard to justify, this is the
comparison to make: does the proposal reach as complete a single source of
truth?

## Pros

- **Genuine single source of truth for colour.** Change `colors.toml` once and
  19 applications follow. That is the whole point, and it is genuinely rare to
  see it done this well.
- **Adding a themed app is a file, not code.** A new `.tpl` is picked up by the
  existing loop. The extension cost is close to zero.
- **Gradients and computed colours work.** The renderer handles
  `{{mix ...}}`, `hypr_gradient`, and friends, so apps that need a derived
  colour get one computed rather than hand-written per theme.
- **It is only 404 lines.** An entire multi-application theming system for
  about the size of one medium panel.
- **Themes are denied code execution**, which is a real threat model applied
  to something most projects never think about: a theme installed from a git
  repo cannot supply Lua, a terminal config, or `vscode.json`, because Hyprland
  runs `hyprland.lua` at login and a VS Code extension is arbitrary JavaScript.

## Cons

- **`sed` as a template engine.** It works and it is fast, but it cannot loop,
  cannot fail loudly on a missing variable, and produces no error when a
  template references a colour the theme does not define. The result is a
  silently half-rendered config.
- **Every new terminal or editor that loads Lua is a code change.** The
  installer maintains an explicit denied list (`INSTALLED_THEME_DENIED`) and the
  comment says so: "Adding a template for another terminal, or for another
  editor that loads Lua, means adding it here." That is a manual step in a
  system that otherwise feels automatic.
- **Adding a *new field* to `colors.toml` means every template is re-read.** The
  renderer greps each `.tpl` for the tokens it needs, which is O(templates ×
  fields) on every theme switch.
- **The 404 lines hide a lot of special cases** — gradient maths, override
  files, `shell.*.toml` handling. It is the most complex single script in the
  system relative to its purpose.

## Risk

**Low, and loud.**

Replacing the template layer breaks theming visibly and immediately: an app
that loses its config reverts to its default colours. Nothing fails quietly
here, which is a good property to have in the layer that owns appearance.

The real risk is in the extension direction — that the denied-list maintenance
notices are treated as routine and a new code-executing config path is allowed
through. That is a security regression, not a styling one.

## Evidence

```bash
# the templates, and the renderer
ls /usr/share/omarchy/default/themed
wc -l /usr/bin/omarchy-theme-set-templates

# the gradient maths and the token grep, in the source
grep -n "mix\|gradient\|GRADIENT" /usr/bin/omarchy-theme-set-templates | head -20

# the denied list, and the comment explaining why it is manual
grep -n -B12 "INSTALLED_THEME_DENIED=" /usr/bin/omarchy-theme-set

# what a template actually looks like
cat /usr/share/omarchy/default/themed/alacritty.toml.tpl
cat /usr/share/omarchy/default/themed/btop.theme.tpl | head -20

# the count
python3 -c "
import json; d=json.load(open('baseline/measurements.json'))['mechanisms']
print(len(d['themedTemplates']), 'templates')"
```

## Amendment history

- 2026-09-30 — initial record.