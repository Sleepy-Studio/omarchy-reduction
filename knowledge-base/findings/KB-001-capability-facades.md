---
id: KB-001-capability-facades
title: The capability facades are the best engineering in the codebase
type: defence
status: accepted
strength: strong
surface: shell, plugins
confidence: high
measuredOn: 2026-09-30
amendments: 0
---

## Problem

Six capability facades sit in `/usr/share/omarchy/shell/services/*Api.qml`:
`PluginAppLibraryApi`, `PluginBarStateApi`, `PluginBarWidgetRegistryApi`,
`PluginFirstPartyServiceApi`, `PluginRegistryApi`, `PluginShellApi`.

Six facades for 35,000 lines of shell looks like over-engineering. The obvious
simplification is to merge them, or to hand plugins the host object directly
and delete the indirection. That would be a reduction in lines and an
**increase in what every plugin can reach**.

`PluginRegistryApi` is the clearest example, and it is about 32 lines. It is
essentially a self-scoped view:

```qml
function isEnabled(id) {
  return String(id || "") === pluginId && enabled
}
function installedPlugins() {          // returns only itself
  var out = ({}); if (manifest) out[pluginId] = manifest; return out
}
```

A third-party plugin asking "is *someone else* enabled?" gets `false`. Asking
for the full plugin list gets a one-entry object. The plugin id is **closed
over, not passed in** — so the plugin cannot widen its own scope by supplying a
different argument. That is the whole design in two functions.

## Proposal

**Do not merge them.** If anything, add facades for host objects that do not
have one, rather than removing any.

The temptation this record exists to resist is the general one: a facade is an
extra layer, and a layer is a cost. Here the layer *is* the security property.
Removing it does not remove a cost, it removes a boundary, and the resulting
system looks the same from outside while being materially weaker.

## Pros

The argument for keeping them is simply that they work, and that they are the
only reason the shell can claim anything about plugins at all.

- A plugin's reach is determined by *which* facade it was handed, not by what
  it asks for.
- The design is honest about its limits. The shell README says plainly that
  this is **not** a QML sandbox — visual plugins share the host object tree.
  A system that states its own boundary is more trustworthy than one that
  implies safety it cannot deliver.

## Cons

The case for change is not empty, and it belongs here.

- **Six near-identical files.** Each is a thin closure. The mechanism could be
  one generic factory parameterised by capability set, which would be smaller
  and would make the *policy* readable in one place instead of six.
- **The security is not enforced, it is arranged.** Because visual plugins
  share the object tree, a determined third-party plugin may well be able to
  reach past its facade. If so, the facades give the *appearance* of a
  boundary without the substance — which is worse than no boundary, because
  it is a boundary people trust.
- **Adding a host capability means adding a facade.** That is friction, and
  friction is where good defaults go to die.
- No test in the shipped source appears to assert that a plugin genuinely
  cannot widen its scope. The property is argued in prose.

That second con is the serious one, and it is the kind of thing that should be
answered by measurement rather than argument: if a plugin can reach the host
object tree, the facade story needs rewording, not defending.

## Risk

**Low risk of changing nothing; high and hard-to-detect risk of changing it.**

Merging facades does not break any plugin — every plugin that works keeps
working. It simply removes a limit none of them were hitting. Nothing fails,
nothing logs, and the reduction is invisible until the first plugin that
depends on the limit.

That is the definition of a silently-wrong change, and it is why this record
exists rather than a commit.

## Evidence

```bash
# the facades and their sizes
wc -l /usr/share/omarchy/shell/services/*Api.qml

# the self-scoped view, verbatim
cat /usr/share/omarchy/shell/services/PluginRegistryApi.qml

# what the host injects for entry points
grep -rn "required property" /usr/share/omarchy/shell/services/Plugin*Api.qml

# the honesty: what the README says about the sandbox
grep -n -i -A3 "not a QML sandbox\|sandbox" /usr/share/omarchy/shell/README.md
```

To answer the serious con — can a plugin actually reach past its facade? —
that needs someone to instrument a third-party plugin and try. Nobody has, as
far as this record knows.

## Amendment history

- 2026-09-30 — initial record.