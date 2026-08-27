# Replacements

## Static replacement sources

A replacement source can provide a static value. This allows a literal to be
copied directly into selected target fields without first storing that value
in another resource. (5.7.0)

Use this capability when the desired source is the literal itself rather than
a field selected from an existing resource.

## Structured data embedded in manifest fields

Replacement target paths can traverse YAML or JSON stored inside a manifest
field. This permits writing a replacement directly into a nested field of the
embedded document. (5.8.0)

For a target `ConfigMap` whose `data.config.json` value contains
`{"config":{"hostname":"..."}}`, the nested hostname can be targeted as
follows:

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

Here, `data.config\\.json.config.hostname` addresses the `config.json` data
key and then traverses to the embedded document's `config.hostname` field.

## Regular-expression selectors

Replacement selectors support regular expressions. One target selector can
therefore match resources using a pattern. (5.8.0)

Use pattern selection when the same replacement should apply to a patterned
set of resource matches.
