# Policy APIs and Migration

## Select a specialized policy kind

Kyverno's CEL-first policy family separates admission tasks by purpose:

| Task | Cluster-scoped kind | Namespaced kind |
| --- | --- | --- |
| Validation | `ValidatingPolicy` | `NamespacedValidatingPolicy` |
| Mutation | `MutatingPolicy` | `NamespacedMutatingPolicy` |
| Generation | `GeneratingPolicy` | `NamespacedGeneratingPolicy` |
| Image verification | `ImageValidatingPolicy` | `NamespacedImageValidatingPolicy` |
| Scheduled deletion | `DeletingPolicy` | `NamespacedDeletingPolicy` |

`PolicyException` attaches exemptions to referenced policies.
`GlobalContextEntry` supplies cached data to CEL expressions.

### Validation

`ValidatingPolicy` introduced CEL validations, Kubernetes-style
`matchConstraints`, and optional generation of native Kubernetes
`ValidatingAdmissionPolicy` resources (since 1.14.0). Existing
`ClusterPolicy` resources remain supported for gradual migration.

```yaml
apiVersion: policies.kyverno.io/v1
kind: ValidatingPolicy
metadata:
  name: check-deployment-replicas
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

### Mutation

`MutatingPolicy` adds CEL-based resource mutation, extended Kyverno CEL
libraries, offline CLI mutation, and generation of native Kubernetes
`MutatingAdmissionPolicy` resources (since 1.15.0).

```yaml
apiVersion: policies.kyverno.io/v1
kind: MutatingPolicy
metadata:
  name: add-default-label
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
  matchConstraints:
    resourceRules:
      - apiGroups: [apps]
        apiVersions: [v1]
        resources: [deployments]
        operations: [CREATE, UPDATE]
```

### Generation

`GeneratingPolicy` expresses resource generation with CEL, including loops and
Kyverno's custom CEL libraries (since 1.15.0). `generator.Apply` can create
resources in a target namespace. This example clones a source Secret whenever
a Namespace is created:

```yaml
apiVersion: policies.kyverno.io/v1
kind: GeneratingPolicy
metadata:
  name: clone-image-pull-secret
spec:
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: [v1]
        operations: [CREATE]
        resources: [namespaces]
  variables:
    - name: targetNs
      expression: object.metadata.name
    - name: sourceSecret
      expression: resource.Get("v1", "secrets", "default", "regcred")
  generate:
    - expression: generator.Apply(variables.targetNs, [variables.sourceSecret])
```

### Scheduled deletion

`DeletingPolicy` is the CEL-based counterpart to `CleanupPolicy` (since
1.15.0). On a cron schedule it evaluates existing resources and deletes those
matching its constraints and conditions:

```yaml
apiVersion: policies.kyverno.io/v1
kind: DeletingPolicy
metadata:
  name: cleanup-old-test-pods
spec:
  schedule: "0 1 * * *"
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: [v1]
        operations: ["*"]
        resources: [pods]
        scope: Namespaced
    namespaceSelector:
      matchLabels:
        environment: test
  conditions:
    - name: isOld
      expression: now() - object.metadata.creationTimestamp > duration("72h")
```

## Choose the API version

The first CEL policy resources used `policies.kyverno.io/v1alpha1` in 1.14.0
and 1.15.0.

In 1.16.0, the cluster-scoped `ValidatingPolicy`, `MutatingPolicy`,
`GeneratingPolicy`, `DeletingPolicy`, and `ImageValidatingPolicy` kinds moved
to `policies.kyverno.io/v1beta1`. `PolicyException` and
`GlobalContextEntry` advanced in step. The promotion plan published with that
release targeted `v1` in 1.17 and general availability in 1.18.

In 1.17.0, the CEL policy APIs became stable under
`policies.kyverno.io/v1`. The promoted family covers cluster-scoped and
namespaced variants of validating, mutating, generating, image-validating,
and deleting policies, plus `PolicyException`. Update manifests from
`v1beta1`; it remains supported during a transition.

```yaml
apiVersion: policies.kyverno.io/v1
kind: ValidatingPolicy
```

## Choose policy scope

`NamespacedValidatingPolicy`, `NamespacedDeletingPolicy`, and
`NamespacedImageValidatingPolicy` became available in 1.16.0. Each mirrors
its cluster-scoped counterpart but applies only within the namespace that
contains it. This supports team-owned enforcement with narrower RBAC.

Namespaced mutating and generating policies were not part of 1.16.0.
`NamespacedMutatingPolicy` and `NamespacedGeneratingPolicy` arrived in
1.17.0, completing the namespaced CEL policy set.

## Migrate legacy policies

`ClusterPolicy` and `CleanupPolicy` are deprecated in 1.17.0 but remain
functional. The schedule is:

- Critical fixes only in 1.18 and 1.19.
- Planned removal in 1.20.
- New policy development on specialized CEL `v1` APIs.
- Legacy `validate.pattern` rules translated to `ValidatingPolicy`
  expressions.

Existing legacy resources remain supported while migration is in progress.

## Pin matching Helm charts

The Kyverno 1.16 chart is `3.6.0`:

```bash
helm repo update
helm upgrade --install kyverno kyverno/kyverno -n kyverno --version 3.6.0
```

The Kyverno 1.17 chart is `3.7.0`:

```bash
helm repo update
helm upgrade --install kyverno kyverno/kyverno -n kyverno --version 3.7.0
```
