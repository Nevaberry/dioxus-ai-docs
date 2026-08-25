---
name: kustomize-knowledge-patch
description: Kustomize
version: 5.8.1
license: MIT
metadata:
  author: Nevaberry
---


# Kustomize Knowledge Patch

Use this skill when working with Kustomize configuration, overlays, edit
commands, replacements, transformers, patches, or Helm chart inflation.

## How to use this skill

1. Identify which part of the kustomization is involved.
2. Start with the upgrade warning below when namespace propagation matters.
3. Apply the quick-reference guidance for the relevant feature.
4. Open the matching reference file for examples, boundaries, and related
   behavior.
5. Keep version-sensitive advice attached to the behavior it affects.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrade-and-namespaces.md](references/upgrade-and-namespaces.md) | Namespace propagation regression, child kustomizations, restored behavior |
| [replacements.md](references/replacements.md) | Static sources, embedded YAML or JSON, selector regular expressions |
| [transformers-and-patches.md](references/transformers-and-patches.md) | Image volumes, empty patch files, strategic-merge deletes |
| [helm-charts.md](references/helm-charts.md) | Development versions, namespace propagation, Helm compatibility |
| [edit-commands.md](references/edit-commands.md) | Label editing, `-f`, `--without-selector` |

## Upgrade safety first

### Namespace propagation to child kustomizations

Treat namespace propagation as a release-sensitive upgrade check.

- Avoid 5.8.0 when workloads require a namespace to propagate to
  child kustomizations.
- That release contains a regression in this behavior.
- Use 5.8.1 when adopting the 5.8 release line for builds that need namespace
  propagation to children.
- The later patch release completes the fix for the regression.

See
[upgrade-and-namespaces.md](references/upgrade-and-namespaces.md)
for the decision boundary.

### Helm compatibility

Helm chart inflation accommodates Helm v4 breaking changes while retaining
support for Helm v3.

When a build invokes chart inflation, do not assume that Helm v4 requires
abandoning Helm v3 compatibility. See
[helm-charts.md](references/helm-charts.md).

## Replacements quick reference

### Use a literal source directly

A replacement source can provide a static value. Use this when a literal
should be copied into selected target fields and there is no reason to place
the value in another resource first.

This removes the need for a source resource whose only purpose is to hold the
literal.

### Write into structured content inside a field

Replacement target paths can traverse YAML or JSON embedded in a manifest
field.

For example, given a target `ConfigMap` whose `data.config.json` value
contains a nested hostname:

```yaml
replacements:
- source:
    kind: ConfigMap
    name: source-configmap
    fieldPath: data.HOSTNAME
  targets:
  - select:
      kind: ConfigMap
      name: target-configmap
    fieldPaths:
    - data.config\\.json.config.hostname
```

The target path reaches `config.hostname` inside the document stored at
`data.config.json`.

See [replacements.md](references/replacements.md) for the supported
replacement-source and target-selection improvements.

### Select targets by pattern

Replacement selectors support regular expressions. A replacement can
therefore select resources by pattern rather than requiring a separate target
selector for each matching resource.

## Transformer and patch quick reference

### Transform image volumes

The `images` transformer updates image references used by Kubernetes image
volumes in addition to the workload image fields it already handled.

If an image change appears incomplete, include image-volume references in the
expected transformed output.

### Accept intentionally empty patch files

Patch files that contain only any of the following are accepted:

- blank lines;
- multiple newlines;
- comments.

These files no longer fail the build merely because they contain no patch
content.

### Delete multiple resources from one patch file

A single patch file can carry multiple strategic-merge patches that use
`$patch: delete`. This arrangement no longer causes a panic.

See
[transformers-and-patches.md](references/transformers-and-patches.md)
for all three behaviors.

## Helm chart quick reference

### Include development chart versions

Set a `helmCharts` entry's version alias to `devel` when development chart
versions should be considered.

### Inherit the top-level namespace

The namespace transformer passes the kustomization's top-level namespace to
`helmCharts` entries. The namespace does not have to be repeated on every
chart:

```yaml
namespace: any-namespace
helmCharts:
- name: minecraft
  repo: https://kubernetes-charts.storage.googleapis.com
  version: v1.2.0
  valuesFile: values.yaml
```

This Helm behavior is separate from the child-kustomization regression
described under upgrade safety.

See [helm-charts.md](references/helm-charts.md) for the combined Helm
guidance.

## Edit-command quick reference

### Keep file-backed label edits consistent

`kustomize edit add labels` handles `-f` in the same way as
`edit add commonLabels`. Use the same flag-dependent expectations for both
commands.

### Add several labels without selectors

`kustomize edit add labels` accepts multiple labels together with
`--without-selector`. This combination no longer fails with a duplicate-key
error.

See [edit-commands.md](references/edit-commands.md) for both label-editing
cases.

## Task routing

Use the smallest relevant reference:

- For an upgrade involving nested kustomizations, open
  [upgrade-and-namespaces.md](references/upgrade-and-namespaces.md).
- For copying or targeting values, open
  [replacements.md](references/replacements.md).
- For image rewriting or patch-file handling, open
  [transformers-and-patches.md](references/transformers-and-patches.md).
- For `helmCharts` configuration or Helm major-version compatibility, open
  [helm-charts.md](references/helm-charts.md).
- For generated label configuration, open
  [edit-commands.md](references/edit-commands.md).

When more than one area is involved, combine the relevant guidance. In
particular, a Helm chart and a child kustomization have distinct namespace
behaviors, so consult both namespace sections when a build contains both.
