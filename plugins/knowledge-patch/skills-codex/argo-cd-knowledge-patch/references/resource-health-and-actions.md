# Resource Health and Actions

## Health and action expansion in 3.2.0

Built-in health support covers:

- DatadogMetric
- GitOps Promoter resources
- 3scale resources
- Coralogix resources
- ExtensionService
- Altinity ClickHouse Operator resources
- CronJobs

Jobs have suspend, resume, and terminate actions. Check for built-in coverage
before retaining a custom health script or Job lifecycle action.

## Health expansion in 3.1.0

Built-in health checks or resource customizations cover:

- SpinApp
- OpenTelemetryCollector
- Logstash
- RabbitMQ topology resources
- Crossplane and Upbound resources
- Kyverno Policy
- Contour HTTPProxy
- Grafana Operator Dashboard and Folder
- Kubernetes Gateway API
- CloudNativePG

KEDA `ScaledObject` health recognizes the `Fallback` condition. Numaplane
resources no longer use a suspended state.

## Scaling and rollout controls

Resource actions can take parameters when scaling workloads (3.1.0). Validate
parameters before invoking an action from automation.

Argo Rollouts resources have `pause` and `skip-current-step` actions (3.1.0).
Numaplane rollouts have a force-promote action (3.0.0). Treat each as an
operator-controlled state transition and capture who invoked it.

## Corrected Config Connector health

Built-in health assessment for `ConfigConnectorContext` and `ConfigConnector`
is corrected in 3.3.13. Remove compensating customizations only after comparing
their behavior with the corrected built-in assessment.

## New health checks in 3.5.0

Built-in health support includes:

- Gardener `Shoot`
- Gateway API `GatewayClass` and `BackendTLSPolicy`
- additional GitOps Promoter resources
- VictoriaMetrics resources
- Karpenter `NodeClaim`

Audit custom Lua health checks for overlap before allowing both implementations
to classify the same resource.

## New actions in 3.5.0

Built-in actions add:

- pause and unpause for `psmdb`
- suspend and resume for MariaDB
- deletion of recyclable Numaflow pipelines
- restart for `StrimziPodSet`
- auto-sync toggling for Applications

Apply the same RBAC, confirmation, and audit expectations used for other
mutating resource actions.

## Corrected health-state semantics

Several health results change in 3.5.0:

- HPA metric failures are degraded.
- CRDs in `Installing` are not degraded.
- Subscriptions requiring manual approval receive appropriate health handling.
- A no-op rehydration no longer leaves a `PromotionStrategy` stuck in
  `Progressing`.

Update alerts and tests that encoded the former states, and compare custom
health overrides with the corrected built-in semantics.
