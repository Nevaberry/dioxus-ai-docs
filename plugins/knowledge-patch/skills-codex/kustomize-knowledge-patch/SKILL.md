---
name: kustomize-knowledge-patch
description: Kustomize
version: 5.8.1
license: MIT
metadata:
  author: Nevaberry
---



# Kustomize Knowledge Patch

## When to use

Load this skill when a Kustomize task involves:

- namespace propagation through child kustomizations or Helm chart inflation;
- Helm chart version selection or Helm runtime compatibility;
- replacement sources, selectors, or structured target fields;
- image rewriting for Kubernetes image volumes;
- patch-file parsing or strategic-merge deletion behavior; or
- scripting `kustomize edit add labels`.

Establish the Kustomize version used by the project or build environment before
applying version-sensitive advice. Give the namespace regression priority during
upgrade reviews because it can change rendered output without requiring a
manifest edit.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/namespaces-and-helm.md](references/namespaces-and-helm.md) | Child namespace regression and fix, Helm namespace propagation, `devel`, Helm v3 and v4 |
| [references/replacements-and-images.md](references/replacements-and-images.md) | Static replacement values, embedded YAML or JSON targets, regular-expression selectors, image volumes |
| [references/patches-and-editing.md](references/patches-and-editing.md) | Empty patch files, multiple strategic-merge deletes, label-edit flag behavior |

## Compatibility first

### Avoid the child-namespace regression

Kustomize 5.8.0 has a namespace-propagation regression for child
kustomizations. If rendered workloads depend on a top-level namespace reaching
children, do not adopt 5.8.0; remain on a suitable earlier release or move to a
fixed release.

Kustomize 5.8.1 completes the fix. Use 5.8.1 when that child propagation is
required and an upgrade into the 5.8 line is otherwise desired.

Do not conflate the child-kustomization regression with Helm chart handling.
In 5.8.0, the namespace transformer also began passing the kustomization's
top-level namespace to `helmCharts`. These are distinct render paths:

| Path | Version-sensitive behavior |
| --- | --- |
| Child kustomization | Broken propagation in 5.8.0; restored in 5.8.1 |
| Helm chart entry | Receives the top-level kustomization namespace in 5.8.0 |

See [references/namespaces-and-helm.md](references/namespaces-and-helm.md) for
the upgrade checks and Helm example.

### Match Helm runtime compatibility

Kustomize 5.8.1 accommodates Helm v4 breaking changes while retaining Helm v3
support. When chart inflation changes after a Helm runtime upgrade, verify the
Kustomize version before rewriting chart configuration.

This compatibility change is separate from chart-version selection. A
`helmCharts` entry may use `devel` as its chart version alias when development
chart versions should be considered.

## Replacement quick reference

### Use a literal source when no resource field is needed

From 5.7.0, a replacement source can provide a static value. Copy the literal
directly to selected target fields instead of first storing it in another
resource solely to serve as the replacement source.

Use this when the source is intrinsically constant. Continue to use a resource
field as the source when the value should be derived from rendered resources.

### Traverse structured text inside a manifest field

From 5.8.0, replacement target paths can enter YAML or JSON serialized inside
a manifest field. For example, a target `ConfigMap` can contain JSON in the
`data.config.json` value while the replacement writes only its nested
`config.hostname` field:

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

The escaped dot keeps `config.json` as the outer field key; the remaining path
addresses the nested structured value.

### Select replacement targets by pattern

From 5.8.0, replacement selectors support regular expressions. Use a pattern
when one replacement should target resources selected by a shared naming or
selection rule rather than enumerating each resource separately.

Keep the two capabilities distinct while debugging:

- selector regular expressions determine which resources are targets;
- structured field paths determine where inside a selected resource the value
  is written.

Full replacement and image-transform guidance is in
[references/replacements-and-images.md](references/replacements-and-images.md).

## Transformer and Helm quick reference

### Rewrite images in image volumes

From 5.7.0, the `images` transformer updates image references used by
Kubernetes image volumes in addition to the workload image fields it already
handled. If an image-volume reference is unexpectedly unchanged, first check
whether the active Kustomize predates this support.

### Let the top-level namespace reach Helm charts

In 5.8.0, a top-level `namespace` is passed to entries in `helmCharts`, so it
does not need to be repeated on each chart:

```yaml
namespace: any-namespace
helmCharts:
- name: minecraft
  repo: https://kubernetes-charts.storage.googleapis.com
  version: v1.2.0
  valuesFile: values.yaml
```

If the same build also contains child kustomizations, account for the separate
5.8.0 child-propagation regression described above.

## Patch and edit quick reference

### Accept intentionally empty patch files

From 5.7.0, a patch file containing only blank lines, repeated newlines, or
comments is accepted rather than causing the build to fail. This permits a
conditionally populated patch file to remain present when it has no active
documents.

### Delete several resources from one patch file

From 5.7.0, one patch file may contain multiple strategic-merge patches that
use `$patch: delete`. This no longer causes Kustomize to panic.

### Keep label-edit flags consistent

From 5.6.0, `kustomize edit add labels` handles `-f` consistently with
`kustomize edit add commonLabels`. Scripts moving between the two edit commands
can rely on the same flag-dependent behavior.

From 5.8.0, `kustomize edit add labels` can add multiple labels together with
`--without-selector` without failing on a duplicate-key error.

See [references/patches-and-editing.md](references/patches-and-editing.md) for
the behavior organized by patch authoring and edit-command automation.

## Task-oriented checks

### When rendered namespaces are wrong

1. Record the exact Kustomize version used for the render.
2. Determine whether the missing namespace is in a child kustomization or a
   Helm chart entry.
3. For a child rendered by 5.8.0, treat the behavior as the known regression
   and move to 5.8.1 when possible.
4. For a Helm chart rendered by 5.8.0, verify that the namespace is declared at
   the kustomization top level before duplicating it on the chart.

### When a replacement misses its target

1. Distinguish source selection from target selection.
2. Use a static source for a literal that does not need to come from a resource.
3. Use a regular expression when the target resources should be matched by a
   pattern.
4. Use a structured field path when the destination lies inside serialized
   YAML or JSON held by a manifest field.
5. Preserve escaping for dots that are part of an outer field key.

### When patch ingestion fails

1. Check whether an intentionally inactive file contains only whitespace or
   comments and whether the Kustomize version includes 5.7.0 behavior.
2. If a file contains several `$patch: delete` documents, check the version
   before splitting a valid multi-delete file as a workaround.

### When label-edit automation fails

1. For `-f`, compare the installed behavior with the 5.6.0 consistency change.
2. For multiple labels combined with `--without-selector`, require the 5.8.0
   duplicate-key fix.

## Scope boundaries

- The 5.8.0 namespace warning applies to propagation into child
  kustomizations; it does not negate the Helm namespace feature in that release.
- Regular-expression support belongs to replacement selectors. Structured-data
  traversal belongs to replacement target field paths.
- The `devel` alias selects development chart versions; Helm v3/v4 support is
  runtime compatibility during chart inflation.
- Empty patch acceptance and multiple `$patch: delete` handling are separate
  parser and execution improvements, even when they occur in the same file.
