# Upgrades and deprecations

## Promtail migration and removal

Promtail was deprecated in 3.4.0 after its code moved into Grafana Alloy. Alloy
provides migration guidance and a configuration-conversion utility.

Promtail is removed as of 3.7.3. Complete migration before adopting a release
with the removal. Lambda-promtail is explicitly outside both the deprecation
and removal and should not be migrated on that basis alone.

## Promtail image tool removal (3.4.0)

The Promtail Docker image no longer contains `wget`. This breaks probes,
scripts, and derived images that invoke it. Replace the dependency or provide
the tool explicitly in a derived image.

## Legacy storage, configuration, and APIs (3.4.0)

The BoltDB store is deprecated together with additional legacy configuration
options and API endpoints. Audit all three surfaces before upgrading; a storage
migration alone does not cover removed configuration or callers of legacy APIs.

## Removed ksonnet configuration (3.5.0)

Deprecated ksonnet configuration is removed. This is a breaking change. Move
remaining deployment generation to a supported mechanism before upgrading.

## Tracing backend migration (3.6.0)

Loki replaces internal OpenTracing with OpenTelemetry. Configuration remains
available through `JAEGER_`-prefixed environment variables, and trace export
remains in Jaeger format. Update observability expectations while preserving
the still-supported configuration contract.

## Meta-monitoring chart migration (3.6.0)

Meta-monitoring responsibilities move from the Grafana meta-monitoring Helm
chart to the Grafana Kubernetes Monitoring Helm chart. Update chart ownership,
values, and automation accordingly.

## Operational UI packaging (3.6.0)

The Operational UI JavaScript moves to a Grafana plugin, but its server APIs
remain in Loki. Helm UI enablement activates those APIs on queriers, and the
gateway routes UI requests to them. Upgrade the client packaging and server
routing together.

## Deployment-mode and community-chart deprecations (3.6.0)

Simple Scalable Deployment mode is deprecated and scheduled for removal before
Loki 4.0.

The community charts `LGTM-distributed`, `loki-canary`, `loki-distributed`, and
`loki-simple-scalable` are also deprecated. Avoid starting new deployments on
these paths and plan migrations for existing installations.

## Open-source chart repository transfer (3.7.0)

Effective March 16, 2026, the open-source Loki Helm chart moved to
`grafana-community/helm-charts` for community maintenance. The GEL chart remains
separately maintained. Update repository references and dependency automation
without redirecting GEL chart sources.

## Parsed-label precedence (3.7.0)

Parsed labels no longer override same-named structured metadata. This breaking
change affects pipelines and queries with collisions. Add explicit tests for
the intended value source.

## Scheduler execution model (3.7.0)

The scheduler now accounts for total compute capacity, and worker threads are
shared across scheduler connections. Both changes are breaking. Revisit sizing,
concurrency, and fairness assumptions during the upgrade.

## Operator breaking changes (3.5.0, 3.7.0)

The Operator's ability to drop OTLP attributes arrives as a breaking ingestion
change. Later, default OpenShift stream labels change as another breaking
update. Inspect generated configuration and dependent queries for both.

## Container working directory (3.7.0)

Loki Dockerfiles set the container working directory to `/`. Derived images and
scripts that use relative paths must resolve them from the filesystem root or
set their own working directory explicitly.
