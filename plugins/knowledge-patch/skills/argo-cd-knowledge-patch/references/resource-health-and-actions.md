# Resource Health and Actions

## Health and customization coverage

Health support and resource customizations expanded substantially in 3.1.0.
Before carrying a custom Lua assessment forward, check for built-in coverage
for:

- SpinApp;
- OpenTelemetryCollector;
- Logstash;
- RabbitMQ topology resources;
- Crossplane and Upbound resources;
- Kyverno Policy;
- Contour HTTPProxy;
- Grafana Operator Dashboard and Folder;
- Kubernetes Gateway API resources; and
- CloudNativePG.

The same 3.1.0 behavior recognizes the `Fallback` condition in KEDA
`ScaledObject` health. Numaplane resources no longer use a suspended state, so
custom health code and dashboards must not depend on that former state.

Built-in health support expanded again in 3.2.0 for:

- DatadogMetric;
- GitOps Promoter resources;
- 3scale resources;
- Coralogix resources;
- ExtensionService; and
- Altinity ClickHouse Operator resources.

CronJobs also gain health assessment in 3.2.0. Prefer maintained built-in
behavior when it meets the resource's semantics, and remove overlapping custom
health scripts only after comparing their healthy, progressing, degraded, and
suspended outcomes.

## Parameterized workload scaling

Resource actions can accept parameters when scaling workloads since 3.1.0.
Define validation and safe bounds for scale inputs rather than treating every
caller-provided parameter as an acceptable replica target.

## Rollout actions

- Numaplane rollout resources gained force-promote actions in 3.0.0. Reserve
  force promotion for an intentional operational override and retain an audit
  trail of the caller and reason.
- Argo Rollouts resources gained `pause` and `skip-current-step` actions in
  3.1.0. `skip-current-step` changes rollout progression rather than merely
  changing presentation state, so protect it with appropriate RBAC.

## Job actions

Jobs gained `suspend`, `resume`, and `terminate` actions in 3.2.0. Distinguish
the desired outcome before invoking one: suspension preserves the Job for
later continuation, resumption restarts progression, and termination is an
explicit end to the active work.
