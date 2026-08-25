# CLI, Reports, Events, and Metrics

## Offline Policy Evaluation

The CLI can evaluate `ValidatingPolicy` and `ImageValidatingPolicy` against
Kubernetes resources or arbitrary JSON payloads, including a Dockerfile
represented as JSON (since 1.14.0). `MutatingPolicy` also supports offline
mutation (since 1.15.0).

Kyverno 1.18.0 broadens `kyverno apply` and `kyverno test` support to:

- cleanup policies;
- HTTP authorization policies;
- Envoy authorization policies;
- `mutateExisting` rules in `MutatingPolicy`.

The `--exceptions-with-policies` option supports test workflows that evaluate
policy exceptions together with their referenced policies.

Offline execution cannot silently reproduce every cluster dependency. Supply
the context required for live Kubernetes reads, cached global context, HTTP
calls, registry metadata, and dynamic certificates, or make the resulting
limitation explicit in the test.

## Report API Group

Kyverno generates `PolicyReport` resources in the `openreports.io` API group
starting in 1.15.0. Use compatible Reports Server and Policy Reporter releases,
and update custom integrations that read the legacy `wgpolicyk8s.io` group.
That legacy group is planned for deprecation.

Results produced by CEL policy types identify the producing type, such as
`source: KyvernoImageValidatingPolicy`. Results also link to evaluated
resources with owner references.

## Exception Results

By default, a matching CEL `PolicyException` records `skip`. Since 1.16.0,
`PolicyException.spec.reportResult` can change that outcome to `pass`:

```yaml
spec:
  reportResult: pass
```

Choose based on how report consumers interpret exemptions; this setting changes
the recorded outcome, not whether the exception matches.

## Suppress Reports Without Disabling Enforcement

Since 1.16.0, adding the `reports.kyverno.io/disabled` label with any value
suppresses both ephemeral reports and persisted `PolicyReport` output. It does
not disable policy enforcement.

```yaml
metadata:
  labels:
    reports.kyverno.io/disabled: "true"
```

The label applies to `ClusterPolicy`, the CEL policy kinds,
`ValidatingAdmissionPolicy`, and `MutatingAdmissionPolicy`. Remove it to resume
reporting.

## Store Only Selected Results

The `--allowedResults` flag, added in 1.17.0, limits which policy outcomes
Kyverno stores in reports. For example, selecting only `Fail` avoids persisting
other result classes and can reduce etcd load in large clusters.

Treat stored-report filtering separately from enforcement, Event generation,
and metrics. Verify every report consumer tolerates absent result classes.

## Kubernetes Events

CEL policies emit Events for passes, violations, evaluation errors, and
compile/load failures as of 1.16.0. Event context includes the policy or rule,
resource, user, and execution mode.

Kyverno 1.18.0 adds the `successEventActions` ConfigMap parameter. Use it to
control which successful policy Events Kyverno emits, reducing noise in large
clusters without suppressing failure reporting.

## CEL Policy Metrics

Kyverno 1.16.0 exposes execution-duration histograms for CEL policies:

```text
kyverno_validating_policy_execution_duration_seconds_{count,sum,bucket}
kyverno_mutating_policy_execution_duration_seconds_{count,sum,bucket}
kyverno_generating_policy_execution_duration_seconds_{count,sum,bucket}
```

Image-validating policies have a corresponding execution-duration histogram.
Labels cover the policy, background mode, resource kind and namespace, request
operation, admission versus background execution, and result. Validating
metrics additionally identify enforce versus audit mode.

Keep metric-label cardinality in mind when building dashboards and alerts,
especially across many namespaces and resource kinds.

## Admission Scaling and Metrics TLS

In 1.18.0, the admission controller can use memory-based HPA autoscaling. The
`/metrics` endpoint also supports TLS.

When enabling metrics TLS, update scrape endpoints, trust material, and
certificate rotation. When enabling memory-based autoscaling, set resource
requests and HPA targets together so utilization has a meaningful denominator.
