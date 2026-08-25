# Runner, Catalog, and Analytics

## View project CI/CD analytics on Dedicated

Since 18.0, a redesigned project CI/CD analytics view is available on GitLab
Dedicated in limited availability. Use it in the project UI to inspect
pipeline performance trends and reliability metrics.

## Inspect CI/CD Catalog component usage

Since 19.0, Ultimate customers on GitLab.com, GitLab Self-Managed, and GitLab
Dedicated can inspect a Catalog resource's usage details. The view identifies
the projects consuming each component, the component version selected by each
consumer, and whether that version is current. Consumers on outdated versions
sort first.

## Export Runner telemetry through OTLP

GitLab Runner 19.0 adds instrumentation feature negotiation, an OTLP export
client, and its first span, `job_execution`. Use these capabilities to export
job execution telemetry to an OTLP-compatible observability system.

## Configure the Runner prepare-stage timeout

GitLab Runner 19.0 makes the prepare-stage timeout configurable in the runner
configuration. Set it there when the default preparation window does not fit
the runner environment.
