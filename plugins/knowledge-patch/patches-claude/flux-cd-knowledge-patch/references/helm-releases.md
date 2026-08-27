# Helm Releases

## Apply and health behavior

### Helm v4 defaults (since 2.8.0)

Flux ships Helm v4. Newly created releases use server-side apply. Releases
already stored by Helm continue to use client-side apply until explicitly
opted in. Kstatus-based health checking is the default for every HelmRelease,
and CEL expressions can define readiness for Helm-managed objects.

Enable the `UseHelm3Defaults` feature gate to retain the previous apply and
health behavior while preparing manifests for the new defaults.

### Post-render hooks (since 2.9.0)

The default HelmRelease post-render strategy is `combined`, so Helm hooks pass
through post-rendering. Set the strategy explicitly to `nohooks` before an
upgrade when a chart depends on hooks bypassing post-rendering.

### Cross-kind and dependency readiness (since 2.7.0 and 2.9.0)

Entries in `HelmRelease.spec.dependsOn` can use CEL expressions to extend
readiness evaluation beyond the dependency's standard Ready condition. CEL
health-check expressions can omit `kind`, applying one expression to all
resource kinds in an API group.

## Failure recovery

### Retry strategy (since 2.7.0)

Set the install or upgrade strategy to `RetryOnFailure` when a failed release
should be retried.

### Cancel stale health checks (since 2.8.0)

The opt-in `CancelHealthCheckOnNewRevision` feature gate covers helm-controller.
It cancels an active health check after any of these inputs change:

- Source revision.
- HelmRelease spec.
- Referenced ConfigMap or Secret.
- Manual reconciliation request.
- Receiver-triggered reconciliation.

Cancellation sets the `Ready` condition reason to `HealthCheckCanceled`.
Enable `DefaultToRetryOnFailure` with this gate; the default no-retry
configuration can otherwise leave the release stuck after cancellation.

## Values and referenced configuration

### Inspect effective values (since 2.5.0)

```shell
flux debug helmrelease --show-values
```

This command displays values after merging inline data with referenced
ConfigMaps and Secrets. Referenced Secret values are printed in clear text, so
protect terminal output, logs, and copied diagnostics.

### Reconcile when values change (since 2.7.0)

Helm-controller can immediately reconcile changes to `valuesFrom` and to both
kubeConfig reference forms. Label an individual referenced object:

```yaml
metadata:
  labels:
    reconcile.fluxcd.io/watch: Enabled
```

Alternatively, set a controller selector such as
`--watch-configs-label-selector=owner!=helm` to watch every matching reference.

### Literal values (since 2.9.0)

`HelmRelease.valuesFrom` supports a literal mode equivalent to
`helm install --set-literal`. The entire content of the selected ConfigMap or
Secret key becomes one string value; Flux does not parse its type or expand
dotted property names.

## Inventory and chart identity

### Managed-resource inventory (since 2.8.0)

Each HelmRelease records its managed objects in `.status.inventory`. Use it to
audit the deployed resource set and to debug ownership or cleanup issues.

### OCI chart digest tracking (since 2.6.0)

Helm-controller normally appends an OCI Helm chart digest to the chart version.
Enable the `DisableChartDigestTracking` feature gate to suppress that behavior.

## ArtifactGenerator chart processing

Since 2.8.0, `ArtifactGenerator` can extract and modify Helm charts while
producing artifacts. A HelmRelease can consume the resulting
`ExternalArtifact` with `spec.chartRef`; see
[Sources and artifacts](sources-and-artifacts.md) for generator composition and
monorepo discovery.
