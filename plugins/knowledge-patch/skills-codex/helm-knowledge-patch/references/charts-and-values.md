# Charts, Templates, and Values

## Chart creation

### Select experimental chart API v3 explicitly

The Helm 4 SDK handles multiple chart API versions (since 4.2.3). Helm 4.2
exposes `helm create --chart-api-version` when the experimental chart v3 gate
is enabled.

Use both the environment gate and the version option:

```sh
HELM_EXPERIMENTAL_CHART_V3=1 helm create demo --chart-api-version v3
```

The option does not enable experimental v3 by itself. Preserve the gate in
scripts and test environments that create v3 charts, and do not assume SDK
code will only encounter one chart API version.

## Template command cleanup

### Remove deprecated note flags

Helm 4.2 deprecates two unused `helm template` flags (since 4.2.3):

- `--hide-notes`
- `--render-subchart-notes`

Remove these flags from scripts, wrappers, CI commands, and documentation.
They should not be retained as required compatibility switches because they
are unused.

## Values coalescing

### Retest chart-default nil handling

Helm 4.2 changes how chart-default nil values are coalesced (since 4.2.3):

- A chart-default `nil` value is no longer copied into the coalesced values.
- `nil` is preserved when the chart default is an empty map.

Retest charts whose overrides rely on nil cleanup, empty-map defaults, or
subchart coalescing. Inspect the final coalesced values and the rendered
manifests; do not assume cleanup follows the earlier behavior.

Useful fixtures include:

1. A scalar or key whose chart default is explicitly `nil`.
2. A key whose chart default is an empty map and whose override is `nil`.
3. A parent/subchart values case that previously depended on nil cleanup.

## Chart file access

### Iterate empty files safely

Helm 3.21.4 prevents `.Files.Lines` from panicking when the requested chart
file is empty. Charts that iterate optional or generated files no longer need
to add content solely to avoid this crash.

Keep an empty-file fixture when the chart supports generated or optional
files. The template should iterate the file successfully and produce the
chart-defined empty result rather than requiring filler content.

## Chart verification

When changing creation, templates, or values:

1. Set `HELM_EXPERIMENTAL_CHART_V3=1` and pass
   `--chart-api-version v3` together for experimental v3 chart creation.
2. Exercise SDK code with every chart API version that the application uses.
3. Remove the deprecated `helm template` note flags from automation.
4. Compare final coalesced values for nil defaults, empty-map defaults, and
   parent/subchart overrides.
5. Render the resulting manifests, not only the intermediate values.
6. Run `.Files.Lines` against an empty chart file on maintained Helm 3 code.
