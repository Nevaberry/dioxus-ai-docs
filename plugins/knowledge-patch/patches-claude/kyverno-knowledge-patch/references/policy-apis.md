# Policy APIs and Exceptions

## API Promotion

The specialized CEL policy family began with
`policies.kyverno.io/v1alpha1` in 1.14.0 for `ValidatingPolicy`,
`ImageValidatingPolicy`, and `PolicyException`. Version 1.15.0 added
`MutatingPolicy`, `GeneratingPolicy`, and `DeletingPolicy` in that API group.

In 1.16.0, the cluster-scoped CEL policy kinds moved to
`policies.kyverno.io/v1beta1`; `PolicyException` and `GlobalContextEntry`
advanced with them. The published promotion plan at that point targeted `v1`
in 1.17 and GA in 1.18.

In 1.17.0, the CEL policy APIs became stable under
`policies.kyverno.io/v1`. This includes cluster-scoped and namespaced variants
of validating, mutating, generating, image-validating, and deleting policies,
plus `PolicyException`. Migrate manifests from `v1beta1`; that version remains
served during a transition period.

Always inspect the target cluster's served CRD versions before applying a
manifest. Existing `ClusterPolicy` resources continue to work during migration.

## Validation

`ValidatingPolicy` expresses validation as CEL and selects requests with
Kubernetes-style `matchConstraints` (since 1.14.0):

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

It can generate a native Kubernetes `ValidatingAdmissionPolicy`, allowing
compatible admission checks to execute inside the API server.

## Mutation

`MutatingPolicy` provides CEL-based mutation, supports Kyverno's extended CEL
libraries and offline CLI mutation, and can generate a native Kubernetes
`MutatingAdmissionPolicy` (since 1.15.0).

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

Kyverno 1.18.0 CLI support includes `mutateExisting` rules in
`MutatingPolicy`.

## Generation

`GeneratingPolicy` expresses generation using CEL, including loops and custom
Kyverno libraries (since 1.15.0). `generator.Apply` can create resources in a
target namespace. This example retrieves a source Secret and clones it when a
Namespace is created:

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

## Scheduled Deletion

`DeletingPolicy` is the CEL counterpart to `CleanupPolicy` (since 1.15.0).
On its cron schedule, it evaluates existing resources and deletes those
matching its constraints and conditions.

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

## Namespaced Policy Kinds

Version 1.16.0 added `NamespacedValidatingPolicy`,
`NamespacedDeletingPolicy`, and `NamespacedImageValidatingPolicy`. They mirror
their cluster-scoped counterparts but apply only in the namespace containing
the policy, enabling team-owned enforcement with narrower RBAC.

Namespaced mutating and generating kinds were not part of 1.16. Version
1.17.0 added `NamespacedMutatingPolicy` and
`NamespacedGeneratingPolicy`, completing the namespaced CEL policy family.
Use them when namespace owners should not have cluster-wide permissions or
effects outside their namespace.

## Policy Exceptions

The CEL-era `PolicyException` identifies target policies through
`spec.policyRefs` and selects exempt resources through CEL
`matchConditions` (since 1.14.0):

```yaml
apiVersion: policies.kyverno.io/v1
kind: PolicyException
metadata:
  name: exclude-skipped-deployment
spec:
  policyRefs:
    - name: ivpol-report-background-sample
      kind: ImageValidatingPolicy
  matchConditions:
    - name: check-name
      expression: object.metadata.name == 'skipped-deployment'
```

Since 1.16.0, an exception can carry image patterns in `spec.images` and
arbitrary values in `spec.allowedValues`. Referenced policies consume this data
as `exceptions.allowedImages` and `exceptions.allowedValues`:

```yaml
apiVersion: policies.kyverno.io/v1
kind: PolicyException
metadata:
  name: allow-ci-latest-images
  namespace: ci
spec:
  policyRefs:
    - name: restrict-image-tag
      kind: ValidatingPolicy
  images:
    - ghcr.io/kyverno/*:latest
  matchConditions:
    - expression: >-
        has(object.metadata.labels.team) &&
        object.metadata.labels.team == 'platform'
```

```cel
string(container.image) in exceptions.allowedImages
capability in exceptions.allowedValues
```

This supports a narrow bypass for a listed image or value rather than exempting
the entire resource. `spec.reportResult` controls the outcome recorded when an
exception matches. Its default is `skip`; use `pass` to record a pass:

```yaml
spec:
  reportResult: pass
```

## Legacy Migration

`ClusterPolicy` and `CleanupPolicy` are deprecated in 1.17.0 but remain
functional. The schedule limits them to critical fixes in 1.18 and 1.19 and
plans removal in 1.20. New policy development should use the specialized CEL
`v1` kinds. Migrate legacy `validate.pattern` rules to `ValidatingPolicy`
expressions.
