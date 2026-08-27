---
name: kyverno-knowledge-patch
description: Kyverno
version: "1.18.0"
license: MIT
metadata:
  author: Nevaberry
---


# Kyverno Knowledge Patch

Use this skill when writing, migrating, testing, or operating Kyverno policies.
Prefer the specialized CEL policy APIs for new work, and check the installed
Kyverno release before selecting an API version or a namespaced policy kind.

## Reference index

| Reference | Topics |
| --- | --- |
| [policy-apis-and-migration.md](references/policy-apis-and-migration.md) | CEL policy kinds, API promotion, namespaced policies, legacy migration, Helm versions |
| [cel-and-exceptions.md](references/cel-and-exceptions.md) | Validation, mutation, generation, deletion, CEL libraries, match conditions, policy exceptions |
| [image-and-http-security.md](references/image-and-http-security.md) | Image verification, attestations, registry credentials, Cosign, outbound HTTP controls |
| [cli-reports-and-operations.md](references/cli-reports-and-operations.md) | CLI behavior, reports, metrics, events, autoscaling, Authz Server, support policy |

## Breaking changes and migration

### Use stable CEL policy APIs

For Kyverno 1.17 and newer, write specialized policies with:

```yaml
apiVersion: policies.kyverno.io/v1
kind: ValidatingPolicy
```

The stable family includes cluster-scoped and namespaced validating, mutating,
generating, image-validating, and deleting policies, plus `PolicyException`.
`v1beta1` remains supported for a transition, but new manifests should use
`v1`.

When supporting Kyverno 1.16, use `policies.kyverno.io/v1beta1`. Earlier
manifests may still use `v1alpha1`; do not copy that version into current
manifests without checking the target cluster.

### Migrate legacy policy kinds

`ClusterPolicy` and `CleanupPolicy` are deprecated as of 1.17. They remain
functional, receive only critical fixes in 1.18 and 1.19, and are planned for
removal in 1.20. Use the specialized CEL `v1` kinds for new policy work.

When migrating a legacy `validate.pattern` rule:

1. Select `ValidatingPolicy` or `NamespacedValidatingPolicy`.
2. Translate the pattern into CEL expressions under `spec.validations`.
3. Move resource selection into Kubernetes-style `matchConstraints`.
4. Test the new policy before replacing the legacy resource.

Legacy policies remain usable during migration; do not require a flag-day
conversion.

### Update report integrations

Policy reports use the `openreports.io` API group. Update consumers that still
expect `wgpolicyk8s.io`, including Reports Server and Policy Reporter
deployments, to compatible releases.

## Choosing a policy kind

| Task | Preferred kind |
| --- | --- |
| Validate resources with CEL | `ValidatingPolicy` or `NamespacedValidatingPolicy` |
| Mutate resources with CEL | `MutatingPolicy` or `NamespacedMutatingPolicy` |
| Generate or clone resources | `GeneratingPolicy` or `NamespacedGeneratingPolicy` |
| Verify images and attestations | `ImageValidatingPolicy` or `NamespacedImageValidatingPolicy` |
| Delete matching resources on a schedule | `DeletingPolicy` or `NamespacedDeletingPolicy` |
| Exempt narrowly selected resources or values | `PolicyException` |

Namespaced policies limit ownership and effects to their containing namespace.
The namespaced validating, image-validating, and deleting kinds are available
in 1.16. Namespaced mutating and generating kinds arrive in 1.17.

## Validation quick start

Use `spec.validations` for CEL assertions and `spec.matchConstraints` for
resource selection:

```yaml
apiVersion: policies.kyverno.io/v1
kind: ValidatingPolicy
metadata:
  name: limit-deployment-replicas
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

Kyverno can generate a native Kubernetes `ValidatingAdmissionPolicy` from this
policy so validation runs in the API server.

## Mutation and generation quick start

`MutatingPolicy` supports CEL-based apply-configuration patches:

```yaml
spec:
  mutations:
    - patchType: ApplyConfiguration
      applyConfiguration:
        expression: >
          Object{
            metadata: Object.metadata{
              labels: Object.metadata.labels{
                environment: "production"
              }
            }
          }
```

`GeneratingPolicy` can fetch a source resource and apply it to a target
namespace:

```yaml
spec:
  variables:
    - name: sourceSecret
      expression: resource.Get("v1", "secrets", "default", "regcred")
  generate:
    - expression: generator.Apply(object.metadata.name, [variables.sourceSecret])
```

Generation expressions can use loops and the extended Kyverno CEL libraries.

## Scheduled deletion quick start

`DeletingPolicy` is the CEL counterpart to `CleanupPolicy`. It evaluates
existing resources on a cron schedule and deletes resources matching its
constraints and conditions:

```yaml
spec:
  schedule: "0 1 * * *"
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: [v1]
        resources: [pods]
        scope: Namespaced
  conditions:
    - name: isOld
      expression: now() - object.metadata.creationTimestamp > duration("72h")
```

## Policy exceptions

Keep exceptions narrow. Use `policyRefs` to name the policy and CEL
`matchConditions` to select resources. An exception may also provide:

- `spec.images`, consumed by the policy as `exceptions.allowedImages`.
- `spec.allowedValues`, consumed as `exceptions.allowedValues`.
- `spec.reportResult: pass` to record a pass instead of the default `skip`.

This allows a policy to bypass only an approved image or value rather than
exempting the whole resource.

## CEL execution guidance

CEL policies can read live Kubernetes resources, cached global context,
external HTTP responses, parsed admission users, parsed image references, and
OCI registry metadata. See the CEL reference before choosing a function.

Extended libraries are also available in policy `matchConditions`. Kyverno
evaluates those conditions itself; it does not translate them into admission
webhook `matchConditions`, so they do not alter webhook routing.

Treat HTTP calls as privileged behavior. Unsafe destinations are blocked by
default in 1.18, and namespaced policies have HTTP disabled by default. Enable
it only with explicit configuration and a deliberate address policy.

## Image verification guidance

Use `ImageValidatingPolicy` to:

- Select image references with globs or CEL.
- Verify signatures and attestations, including SBOMs.
- Extract images from arbitrary JSON payloads.
- Supply verification certificates dynamically through CEL.

Image verification supports Cosign v3 features. For legacy `ClusterPolicy`
verification, registry credential secrets may use `namespace/name`, and
Kyverno can automatically use a Pod's `imagePullSecrets`.

## CLI checks

Use `kyverno apply` and `kyverno test` before installing policies. The CLI can
evaluate CEL validating and image policies against arbitrary JSON and can
perform offline mutation.

Current CLI support also covers cleanup policies, HTTP and Envoy authorization
policies, and `mutateExisting` rules in `MutatingPolicy`. Use
`--exceptions-with-policies` when testing policy-exception workflows.

## Reports, events, and metrics

To reduce report storage, use `--allowedResults` to retain only selected
outcomes. To suppress reports for one policy without disabling enforcement,
add:

```yaml
metadata:
  labels:
    reports.kyverno.io/disabled: "true"
```

The label suppresses ephemeral and persisted policy reports. Remove it to
resume reporting.

CEL policies expose execution-duration histograms and emit Kubernetes Events
for evaluation results and policy load or compile failures. Configure
`successEventActions` to reduce successful-event noise while keeping failure
reporting.

The admission controller supports memory-based HPA autoscaling, and the
`/metrics` endpoint can use TLS.

## Operational compatibility

Kyverno 1.16 uses chart `3.6.0`; Kyverno 1.17 uses chart `3.7.0`. Pin the chart
version that matches the intended application release during upgrades.

Starting with 1.18, community patch support covers only the current and
immediately previous releases for roughly three months, and fixes in that
window are limited to critical or high-severity CVEs and other critical
issues. Plan frequent upgrades or arrange longer-term commercial support.
