# Charts, Templates, and Values

This reference organizes chart-facing guidance from batch `4.2.3`.

## Experimental chart API v3

The Helm 4 SDK can handle multiple chart API versions.

Helm 4.2 exposes `helm create --chart-api-version` when the experimental v3
gate is enabled. Creating a v3 chart requires both the gate and the option:

```sh
HELM_EXPERIMENTAL_CHART_V3=1 helm create demo --chart-api-version v3
```

Keep these conditions distinct:

- `HELM_EXPERIMENTAL_CHART_V3=1` enables the experimental v3 path.
- `--chart-api-version v3` requests v3 for the chart being created.
- The SDK's multiple-version support is the broader embedding capability.

Do not assume the creation option is generally available without the
experimental gate.

## Deprecated template note flags

Helm 4.2 deprecates two unused `helm template` flags:

- `--hide-notes`
- `--render-subchart-notes`

Scripts should stop relying on or passing these flags. When updating a
wrapper:

1. Remove the flags from generated command lines.
2. Remove configuration fields whose only purpose is to select them.
3. Update command assertions and fixtures that expect them.

Their deprecation is tied to the flags being unused; do not preserve them as
if they still control required rendering behavior.

## Nil values during coalescing

Helm 4.2 changes how chart-default nil values participate in values
coalescing:

- Chart-default `nil` values are no longer copied into coalesced values.
- When the chart default is an empty map, `nil` is preserved.

Retest charts when their overrides depend on:

- Nil cleanup.
- An empty-map default.
- Subchart values coalescing.

Inspect the resulting coalesced values in those cases. Do not assume a nil
value will be copied from chart defaults or cleaned up exactly as it was
before this change.

## Focused chart review

A Helm 4 major-version migration does not automatically require every Helm 3
chart to change. For chart-focused work, prioritize concrete affected areas:

- Experimental chart API version selection.
- Automation that still passes deprecated template note flags.
- Overrides and subcharts that depend on nil coalescing.
- Packaging workflows that expect reproducible archives.
- Cache workflows that assume identity follows source location.

The packaging and caching behaviors are detailed in
[operations-and-delivery.md](operations-and-delivery.md).
