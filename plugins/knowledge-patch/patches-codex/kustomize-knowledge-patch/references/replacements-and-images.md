# Replacements and image transforms

Use this reference when a transformation needs a literal input, pattern-based
target selection, a destination inside serialized data, or an image reference
stored in a Kubernetes image volume.

## Static replacement sources

From 5.7.0, a replacement source may provide a static value. This allows a
literal value to be copied into the selected target fields without first
placing that value in another resource.

Choose the source form according to where the value belongs:

- use a static value when it is an intrinsic literal for the customization;
- use a resource-backed source when the value should be copied from a field in
  a rendered resource.

The static source removes the need for a staging resource whose only purpose is
to carry a replacement value.

## Structured YAML or JSON target data

From 5.8.0, replacement target paths can traverse YAML or JSON serialized
inside a manifest field. The replacement can update one nested value without
treating the entire serialized document as the destination.

For a target `ConfigMap` whose `data.config.json` value contains a structure
such as `{"config":{"hostname":"..."}}`, target the nested hostname as follows:

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

Read the target path in two stages:

1. `data.config\\.json` identifies the outer manifest field, preserving the dot
   in the `config.json` key.
2. `config.hostname` traverses the structured document stored in that field.

Use this support when only a nested field should change. Preserve the path
escaping so the outer key is not interpreted as additional path segments.

## Regular expressions in target selectors

From 5.8.0, replacement selectors support regular expressions. A selector can
therefore match a set of target resources by pattern instead of requiring each
resource to be named individually.

Pattern selection and structured traversal solve different parts of a
replacement:

| Stage | Capability |
| --- | --- |
| Choose resources | Regular expressions in replacement selectors |
| Choose the nested destination | Field paths that traverse embedded YAML or JSON |
| Supply a constant | Static replacement source |

When diagnosing an unchanged target, inspect the stages separately: confirm
that the selector matches the resource, then confirm that the field path
reaches the intended destination.

## Image references in Kubernetes image volumes

From 5.7.0, the `images` transformer updates references used by Kubernetes
image volumes as well as the workload image fields supported previously.

For builds that contain image volumes:

1. Keep the image rewrite in the normal `images` transformer configuration.
2. Ensure the active Kustomize includes the 5.7.0 image-volume support.
3. Inspect the rendered image-volume reference along with the other rewritten
   image fields.

If workload container images change but an image-volume reference does not,
the Kustomize version is a relevant compatibility check.
