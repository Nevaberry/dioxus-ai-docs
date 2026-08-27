# CLI, Reports, and Operations

## Test policies before installation

The Kyverno CLI can evaluate `ValidatingPolicy` and
`ImageValidatingPolicy` against arbitrary JSON payloads, including a
Dockerfile represented as JSON (since 1.14.0). This supports pre-cluster
testing of policy behavior.

`MutatingPolicy` supports offline CLI mutation (since 1.15.0).

As of 1.18.0, `kyverno apply` and `kyverno test` also handle:

- Cleanup policies.
- HTTP authorization policies.
- Envoy authorization policies.
- `mutateExisting` rules in `MutatingPolicy`.

Use `--exceptions-with-policies` for policy-exception test workflows.

## Consume policy reports

CEL validating and image-validating policy results identify their producing
policy type. For example, an image-validation result may use
`source: KyvernoImageValidatingPolicy`. Results link to evaluated resources
with owner references (since 1.14.0).

Kyverno generates `PolicyReport` resources in the `openreports.io` API group
(since 1.15.0). Use compatible Reports Server and Policy Reporter releases,
and update integrations from the legacy `wgpolicyk8s.io` group, which is
planned for deprecation.

### Filter stored results

The `--allowedResults` flag limits which policy outcomes are stored in reports
(since 1.17.0). For example, selecting only `Fail` avoids storing other result
classes and can reduce etcd load in large clusters.

### Suppress reports per policy

Add the `reports.kyverno.io/disabled` label with any value to suppress both
ephemeral reports and `PolicyReport` output without disabling enforcement
(since 1.16.0):

```yaml
metadata:
  labels:
    reports.kyverno.io/disabled: "true"
```

The label applies to `ClusterPolicy`, CEL policy kinds,
`ValidatingAdmissionPolicy`, and `MutatingAdmissionPolicy`. Remove the label
to resume reporting.

## Observe CEL policies

Kyverno exposes execution-duration histograms for validating, mutating,
generating, and image-validating CEL policies (since 1.16.0):

```text
kyverno_validating_policy_execution_duration_seconds_{count,sum,bucket}
kyverno_mutating_policy_execution_duration_seconds_{count,sum,bucket}
kyverno_generating_policy_execution_duration_seconds_{count,sum,bucket}
```

Metric labels cover:

- Policy identity.
- Background mode.
- Resource kind and namespace.
- Request operation.
- Admission versus background execution.
- Result.
- Enforce versus audit mode for validating metrics.

CEL policies also emit Kubernetes Events for passes, violations, evaluation
errors, and compile or load failures. Event context includes policy or rule,
resource, user, and mode.

The `successEventActions` ConfigMap parameter controls which successful policy
events Kyverno emits (since 1.18.0). Use it to reduce event noise in large
clusters without suppressing failure reporting.

## Scale and secure metrics

The admission controller supports memory-based HPA autoscaling, and the
`/metrics` endpoint supports TLS (since 1.18.0).

## Run service-edge authorization

The Kyverno Authz Server evaluates Kyverno policies for Envoy's External
Authorization filter or operates as a standalone HTTP authorization service
(since 1.16.0).

The companion Go SDK can:

- Load and compile policies.
- Evaluate incoming requests into structured allow or deny results.
- Integrate optional metrics or hooks.
- Serve gateway, sidecar, and application-middleware integrations.

CEL API types live in the lightweight `kyverno/api` repository, while the
Kyverno SDK lives in `kyverno/sdk` for controller and integration consumers
(since 1.17.0).

## Customize the policies chart

The policies Helm chart can configure `ValidatingPolicy` exclusions by:

- Namespace.
- Subject.
- Resource rules.
- Match conditions.

It also supports `auditAnnotation` configuration and per-policy annotation
overrides (since 1.18.0).

## Plan the upgrade cadence

Starting with 1.18.0, community patch support covers only the current and
immediately previous releases for roughly three months. Patches in that window
are limited to critical or high-severity CVEs and other critical fixes.
Operators should plan frequent upgrades or obtain longer-term commercial
support.
