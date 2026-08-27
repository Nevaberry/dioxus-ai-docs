# Charts, Templates, and Values

Use this reference when creating charts, maintaining template automation,
coalescing values, or reading optional and generated chart files.

## Chart creation

### Experimental chart API v3 *(since 4.2.3)*

Helm 4's SDK supports multiple chart API versions. Helm 4.2 exposes
`helm create --chart-api-version` when the experimental chart API v3 gate is
enabled.

Enable the gate and select v3 explicitly:

```sh
HELM_EXPERIMENTAL_CHART_V3=1 helm create demo --chart-api-version v3
```

Treat both inputs as required. `--chart-api-version v3` does not by itself
enable the experimental feature. Code that consumes the created chart should
also avoid assuming that only one chart API version can appear.

## Template automation

### Deprecated note flags *(since 4.2.3)*

Helm 4.2 deprecates these unused `helm template` flags:

- `--hide-notes`
- `--render-subchart-notes`

Remove them from scripts, wrappers, CI invocations, and command builders. Do
not treat either flag as a required way to control rendered notes because the
flags are unused.

## Values coalescing

### Chart-default `nil` behavior *(since 4.2.3)*

Helm 4.2 changes two nil-handling cases during values coalescing:

- chart-default `nil` values are no longer copied into coalesced values;
- `nil` is preserved when the chart default is an empty map.

Retest charts whose overrides depend on nil cleanup or subchart coalescing.
Inspect the final coalesced values and rendered output rather than inferring
behavior from the input values alone.

Useful fixtures include:

1. a default key whose value is explicitly `nil`;
2. a default empty map with a `nil` override;
3. the same shapes passed through a subchart boundary;
4. templates that distinguish an absent key, `nil`, and an empty map.

## Chart files

### Empty files with `.Files.Lines` *(since 3.21.4)*

`.Files.Lines` no longer panics when the requested chart file is empty. Charts
that iterate optional or generated files do not need to add content solely to
avoid this crash.

Keep explicit chart behavior for semantically required content. The absence of
a panic means an empty file can be iterated safely; it does not mean every
empty configuration file is valid for the application that consumes it.

Test at least these cases:

- an empty file that is intentionally optional;
- a generated file that occasionally has no lines;
- a non-empty file to preserve normal line iteration;
- any template fallback that should run when iteration produces no entries.

## Chart verification checklist

- Enable the experimental gate before requesting chart API v3.
- Pass `--chart-api-version v3` explicitly when v3 output is intended.
- Make SDK consumers tolerate the selected chart API version.
- Remove both deprecated note flags from template automation.
- Inspect coalesced values for explicit `nil`, empty maps, and subcharts.
- Render templates that distinguish missing, nil, and empty-map values.
- Exercise `.Files.Lines` with both empty and non-empty files.
- Preserve application validation for files that must not be empty.
