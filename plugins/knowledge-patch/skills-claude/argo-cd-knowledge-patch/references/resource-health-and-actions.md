# Resource Health and Actions

Prefer built-in health checks and actions over overlapping custom Lua. When
moving from a customization to a built-in implementation, compare state names,
transition timing, and action parameters before deleting the customization.

## Health coverage

### Operator and platform resources

Argo CD 3.1.0 adds built-in health checks or customizations for:

- SpinApp, OpenTelemetryCollector, Logstash, and RabbitMQ topology resources;
- Crossplane and Upbound resources;
- Kyverno Policy and Contour HTTPProxy;
- Grafana Operator Dashboard and Folder;
- Kubernetes Gateway API and CloudNativePG.

KEDA `ScaledObject` health recognizes the `Fallback` condition, and Numaplane
resources no longer use a suspended state.

Argo CD 3.2.0 adds health support for DatadogMetric, GitOps Promoter, 3scale,
Coralogix, ExtensionService, and Altinity ClickHouse Operator resources.
CronJobs also gain health assessment.

In 3.3.13, built-in assessment is corrected for `ConfigConnectorContext` and
`ConfigConnector` resources.

### Additional resource families

Argo CD 3.5.0 adds health support for:

- Gardener `Shoot`;
- Gateway API `GatewayClass` and `BackendTLSPolicy`;
- additional GitOps Promoter resources;
- VictoriaMetrics resources;
- Karpenter `NodeClaim`.

## Corrected health states

In 3.5.0:

- HPA metric failures are recognized as degraded;
- CRDs in `Installing` are not marked degraded;
- manual-approval Subscription health is handled;
- a no-op rehydration no longer leaves a `PromotionStrategy` stuck in
  `Progressing`.

Remove local workarounds only after confirming dashboards and automation accept
the corrected state transitions.

## Scaling and rollout actions

Resource scaling actions accept parameters as of 3.1.0. Validate parameter
names and bounds at the caller because an action can now express more than one
fixed scaling operation.

Argo Rollouts resources add `pause` and `skip-current-step` actions in 3.1.0.
Numaplane rollouts add a force-promote action in 3.0.0. Apply promotion and
flow-control actions only after checking current rollout state and recovery
options.

## Job and database lifecycle actions

Jobs gain suspend, resume, and terminate actions in 3.2.0.

In 3.5.0, actions add:

- pause and unpause for `psmdb`;
- suspend and resume for MariaDB;
- deletion of recyclable Numaflow pipelines;
- restart for `StrimziPodSet`;
- auto-sync toggling for Applications.

Treat terminate, delete, restart, and auto-sync actions as state-changing
operations. Confirm the selected object, namespace, and present health before
execution, and verify the post-action state.
