---
name: kyverno-knowledge-patch
description: Kyverno
version: 1.18.0
license: MIT
metadata:
  author: Nevaberry
---


# Kyverno Knowledge Patch

Use this skill when creating, reviewing, testing, or operating Kyverno policies,
especially the specialized CEL policy APIs. Prefer the project's manifests,
installed CRDs, Helm values, and observed behavior when they disagree with this
guidance.

## How to Use This Skill

1. Determine the installed Kyverno and chart versions before changing API
   versions or values.
2. Identify whether the policy is a specialized CEL policy or a legacy
   `ClusterPolicy`/`CleanupPolicy`.
3. Choose cluster-scoped or namespaced policy kinds deliberately.
4. Check whether expressions rely on Kyverno CEL extensions, network access,
   registry credentials, or exception-provided data.
5. Exercise the policy with `kyverno apply` or `kyverno test`, then verify
   reports, Events, and metrics in the cluster.
6. Open the topic reference for complete syntax and operational constraints.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Policy APIs](references/policy-apis.md) | CEL policy kinds, API promotion, scope, mutation, generation, deletion, exceptions, legacy migration |
| [CEL and authorization](references/cel-and-authorization.md) | Extended libraries, utility functions, `matchConditions`, HTTP hardening, gzip, Authz Server |
| [Image verification](references/image-verification.md) | `ImageValidatingPolicy`, signatures, attestations, Cosign v3, registry credentials |
| [CLI, reports, and observability](references/cli-reports-observability.md) | Offline evaluation, report APIs and filtering, Events, metrics, autoscaling, metrics TLS |
| [Operations and upgrades](references/operations-and-upgrades.md) | Helm chart versions, chart customization, API/SDK repositories, deprecation and support windows |

## Breaking Changes and Deprecations

### Use the API Version Installed by the Target Cluster

The specialized policy API changed as it matured:

| Kyverno release | Manifest API guidance |
| --- | --- |
| 1.14–1.15 | Initial kinds use `policies.kyverno.io/v1alpha1` |
| 1.16 | Cluster-scoped CEL kinds, `PolicyException`, and `GlobalContextEntry` use `v1beta1` |
| 1.17 onward | CEL policy kinds and `PolicyException` use stable `policies.kyverno.io/v1` |

Do not copy a newer `apiVersion` into a cluster whose CRDs do not serve it.
During the 1.17 transition, update manifests to `v1`; `v1beta1` remains
temporarily supported.

### Migrate Legacy Policy Kinds

`ClusterPolicy` and `CleanupPolicy` are deprecated in 1.17. They remain
functional, receive only critical fixes in 1.18 and 1.19, and are planned for
removal in 1.20. Write new policies with the specialized CEL `v1` APIs.
Translate legacy `validate.pattern` rules into `ValidatingPolicy` CEL
expressions.

### Read Reports from OpenReports

Starting in 1.15, Kyverno writes `PolicyReport` resources in the
`openreports.io` API group. Upgrade Reports Server, Policy Reporter, and custom
integrations that still read `wgpolicyk8s.io`; that legacy group is planned for
deprecation.

### Treat Policy HTTP as Privileged I/O

In 1.18, HTTP CEL calls are constrained by configurable address allowlists and
blocklists. Unsafe destinations such as loopback and metadata services are
blocked by default. Namespaced policies cannot make HTTP calls unless explicitly
enabled, and outbound calls use a separately scoped token.

### Plan Frequent Patch Upgrades

From 1.18, community patch support covers the current and immediately previous
release for roughly three months. Patches in that window are limited to critical
or high-severity CVEs and other critical fixes.

## Choose the Specialized Policy Kind

| Task | Cluster-scoped kind | Namespaced kind |
| --- | --- | --- |
| Validate resources with CEL | `ValidatingPolicy` | `NamespacedValidatingPolicy` |
| Mutate resources with CEL | `MutatingPolicy` | `NamespacedMutatingPolicy` |
| Generate resources with CEL | `GeneratingPolicy` | `NamespacedGeneratingPolicy` |
| Verify images | `ImageValidatingPolicy` | `NamespacedImageValidatingPolicy` |
| Delete resources on a schedule | `DeletingPolicy` | `NamespacedDeletingPolicy` |

Namespaced validating, deleting, and image-validating kinds arrived in 1.16.
Namespaced mutation and generation arrived in 1.17. Use namespaced kinds when
team ownership and narrower RBAC are required; their effects stay within their
namespace.

Existing `ClusterPolicy` resources remain supported during migration. A
`ValidatingPolicy` can generate a native Kubernetes
`ValidatingAdmissionPolicy`, and a `MutatingPolicy` can generate a native
`MutatingAdmissionPolicy`, moving compatible admission work into the API
server.

## Quick Policy Patterns

### CEL Validation

```yaml
apiVersion: policies.kyverno.io/v1
kind: ValidatingPolicy
metadata:
  name: cap-replicas
spec:
  validations:
    - expression: object.spec.replicas <= 5
      message: The number of replicas must not exceed 5
  matchConstraints:
    resourceRules:
      - apiGroups: [apps]
        apiVersions: [v1]
        resources: [deployments]
```

### Apply-Configuration Mutation

`MutatingPolicy` supports CEL-computed `ApplyConfiguration` patches, offline CLI
mutation, Kyverno CEL libraries, and native admission-policy generation.

```yaml
spec:
  mutations:
    - patchType: ApplyConfiguration
      applyConfiguration:
        expression: Object{metadata: Object.metadata{labels: {"environment": "production"}}}
```

### CEL Generation

`GeneratingPolicy` supports loops and custom CEL libraries.
`generator.Apply(namespace, resources)` can create resources in a target
namespace, including cloning a source Secret when a Namespace is created.

```cel
generator.Apply(object.metadata.name, [variables.sourceSecret])
```

### Scheduled Deletion

`DeletingPolicy` is the CEL counterpart to `CleanupPolicy`. It evaluates
existing resources on `spec.schedule` and deletes objects that match its
constraints and conditions.

```yaml
spec:
  schedule: "0 1 * * *"
  conditions:
    - name: isOld
      expression: now() - object.metadata.creationTimestamp > duration("72h")
```

## Use Narrow Exceptions

The CEL-era `PolicyException` selects policies with `spec.policyRefs` and
resources with CEL `matchConditions`. Since 1.16 it can also supply approved
image patterns through `spec.images` and arbitrary values through
`spec.allowedValues`.

Consume those values as `exceptions.allowedImages` and
`exceptions.allowedValues` in the referenced policy. This bypasses only a
specific image or value instead of exempting the entire resource.

`spec.reportResult` controls the recorded result for a match. The default is
`skip`; set it to `pass` when report consumers require a passing outcome.

## Use Extended CEL Deliberately

Kyverno CEL policies can read live Kubernetes resources, call external HTTP
services, parse admission users and image references, use cached
`GlobalContextEntry` data, and inspect OCI registry metadata. Later additions
include hashing, rounding, X.509 decoding, random strings, list-to-map
conversion, JSON/YAML parsing, time helpers, and gzip operations.

Kyverno libraries are also available in policy `matchConditions`. Kyverno
evaluates those expressions itself; it does not translate them into admission
webhook `matchConditions`, so they do not alter webhook routing.

Audit every expression for permissions, network policy, failure behavior, and
offline-test fidelity. See the CEL reference for exact function names.

## Verify Images with the Right API

Prefer `ImageValidatingPolicy` for new image verification. It can:

- select image references using globs or CEL;
- verify signatures and attestations such as SBOMs;
- extract images from arbitrary JSON payloads;
- obtain certificates dynamically through CEL;
- use Cosign v3 verification features.

For legacy `ClusterPolicy` image verification in 1.18,
`imageRegistryCredentials.secrets` accepts `namespace/name` references, and
Kyverno automatically tries a Pod's `imagePullSecrets`.

## Test Before Admission

Use `kyverno apply` and `kyverno test` for pre-cluster checks. The CLI evaluates
CEL validating and image policies against Kubernetes resources or arbitrary
JSON payloads. By 1.18 it also handles cleanup policies, HTTP and Envoy
authorization policies, and `mutateExisting` rules in `MutatingPolicy`.

Use `--exceptions-with-policies` for policy-exception test workflows. Remember
that offline evaluation may need explicit context for live resource reads,
HTTP, registry data, or dynamically supplied certificates.

## Control Reporting and Event Volume

- Label a policy `reports.kyverno.io/disabled` with any value to suppress both
  ephemeral and persisted reports without disabling enforcement.
- Use `--allowedResults` to limit which result classes are stored; retaining
  only `Fail` can substantially reduce etcd load.
- Use the `successEventActions` ConfigMap parameter to reduce successful-policy
  Event noise without suppressing failure reporting.

CEL policy reports identify the producing policy type and attach owner
references to evaluated resources. CEL policies emit Events for passes,
violations, evaluation errors, and compile/load failures.

## Observe and Operate

Execution-duration histograms exist for validating, mutating, generating, and
image-validating CEL policies. Their labels describe policy, background mode,
resource kind and namespace, request operation, execution path, and result;
validating metrics also distinguish enforce from audit.

In 1.18, the admission controller supports memory-based HPA autoscaling and the
`/metrics` endpoint supports TLS. Coordinate scrape configuration and
certificates when enabling metrics TLS.

For Envoy or service-edge enforcement, use the Kyverno Authz Server as an
External Authorization endpoint or standalone HTTP authorization service. The
companion Go SDK can compile and evaluate policies and expose structured
allow/deny results with optional metrics and hooks.
