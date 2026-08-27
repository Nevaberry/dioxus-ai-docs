# Migrations and Breaking Changes

Use this reference before upgrading Loki binaries, charts, Operator-managed
stacks, images, or configuration. The changes are grouped by migration task;
version annotations identify when the guidance became relevant.

## Migrate Promtail to Grafana Alloy

Promtail was deprecated in 3.4.0 because its code moved into Grafana Alloy.
Alloy provides migration guidance and a configuration-conversion utility.
Lambda-promtail is a separate component and is explicitly outside this
deprecation.

Promtail was removed as of 3.7.3. Complete the Alloy migration before adopting
a Loki distribution that no longer ships it; do not infer that Lambda-promtail
was removed.

Also audit tooling layered onto the Promtail image. Since 3.4.0, its Docker
image no longer contains `wget`. Replace probes or scripts that invoke it, or
add the required binary explicitly to a derived image.

## Retire legacy stores, configuration, and endpoints

The BoltDB store, additional legacy configuration options, and legacy API
endpoints are deprecated as of 3.4.0. Inventory them together because a stack
may have migrated its index store while retaining obsolete configuration or
clients that still call a legacy endpoint.

Deprecated ksonnet configurations were removed in 3.5.0. Replace those
deployment definitions rather than expecting compatibility aliases.

## Update chart values and ownership assumptions

In 3.5.0, object-store values use `object_store.storage_prefix` instead of
`object_store.prefix`. Rename the key and render the chart to verify the
generated storage configuration.

Installation ownership also differs from older templates: since 3.4.0, the
installation manager sets `managed-by`; the chart template does not. ConfigMap
and Secret checksums cover `.data` only, so metadata-only changes do not imply
the same rollout checksum behavior.

The open-source Loki chart moved to `grafana-community/helm-charts` on March
16, 2026, as documented with 3.7.0. Update repository references, dependency
sources, and automation. The GEL chart remains separately maintained.

## Replace deprecated deployment modes and charts

Simple Scalable Deployment mode is deprecated as of 3.6.0 and scheduled for
removal before Loki 4.0. Plan a deployment-mode migration rather than building
new long-lived automation around it.

The community charts `LGTM-distributed`, `loki-canary`, `loki-distributed`, and
`loki-simple-scalable` are also deprecated as of 3.6.0. Move values and release
automation to a maintained chart, validating resource names and topology as
part of the migration.

Meta-monitoring responsibilities moved from the Grafana meta-monitoring Helm
chart to the Grafana Kubernetes Monitoring Helm chart in 3.6.0-era guidance.
Move monitoring values and ownership to the latter chart.

## Account for label precedence changes

Parsed labels no longer override same-named structured metadata in 3.7.0; this
is a breaking change. Review pipelines that create both forms of a key and
update queries, retention rules, templates, dashboards, and golden tests to
use the structured-metadata value when the names collide.

This precedence rule is separate from the ingestion-side duplicate suppression
that avoids emitting metadata twice when a key comes from both stream labels
and extracted fields.

## Re-size scheduler execution

Two scheduler engine changes in 3.7.0 are classified as breaking:

- scheduling accounts for total compute capacity;
- worker threads are shared across all scheduler connections.

Revisit capacity models, connection-count assumptions, concurrency settings,
and performance baselines. Do not multiply a worker-thread setting by the
number of scheduler connections when estimating available execution.

## Review Operator migrations

Operator support for dropping OTLP attributes arrived with a breaking
classification in 3.5.0. Confirm which attributes are removed and update any
labeling, structured-metadata, routing, or query dependencies before enabling
the generated configuration.

Default OpenShift stream labels changed as a breaking update in 3.7.0. Validate
selectors, alert rules, dashboards, retention, and tenant behavior that depend
on those defaults.

On OCP 4.20, the Operator no longer deploys NetworkPolicies automatically.
Create policies explicitly if the stack relies on network isolation; do not
interpret absence as an instruction to run without equivalent controls.

## Update tracing integrations

Loki switched its internal tracing backend from OpenTracing to OpenTelemetry in
3.6.0. Existing configuration remains available through `JAEGER_`-prefixed
environment variables, and traces continue to export in Jaeger format. Update
instrumentation expectations without unnecessarily renaming a still-supported
configuration surface.

## Fix relative paths in derived containers

Loki Dockerfiles set the container working directory to the filesystem root in
3.7.0. Audit derived images, entrypoints, mounted configuration, and scripts
that use relative paths. Resolve important paths explicitly so they do not
silently move under `/`.

## Migration validation checklist

- Confirm no required deployment depends on removed Promtail or ksonnet
  artifacts.
- Search images and probes for `wget` and scripts for working-directory
  assumptions.
- Rename `object_store.prefix` and render storage configuration.
- Update chart repositories and deprecated chart dependencies.
- Identify BoltDB, legacy configuration, legacy API, and Simple Scalable
  dependencies.
- Re-run label-collision and query tests after the precedence change.
- Load-test the scheduler using total capacity and shared workers.
- Diff Operator-generated OTLP and OpenShift labeling and networking resources.
