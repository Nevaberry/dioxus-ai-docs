# Admission Policies

## MutatingAdmissionPolicy (beta 1.34)

Declarative CEL-based mutations, replacing mutating webhooks. Requires feature gate `MutatingAdmissionPolicy` and `--runtime-config=admissionregistration.k8s.io/v1beta1=true`.

```yaml
apiVersion: admissionregistration.k8s.io/v1beta1
kind: MutatingAdmissionPolicy
metadata:
  name: add-team-label
spec:
  matchConstraints:
    resourceRules:
      - apiGroups: ["apps"]
        apiVersions: ["v1"]
        operations: ["CREATE"]
        resources: ["deployments"]
  mutations:
    - patchType: ApplyConfiguration
      applyConfiguration:
        expression: >
          Object{
            metadata: Object.metadata{
              labels: {"team": "platform"}
            }
          }
---
apiVersion: admissionregistration.k8s.io/v1beta1
kind: MutatingAdmissionPolicyBinding
metadata:
  name: add-team-label-binding
spec:
  policyName: add-team-label
  matchResources: {}
```

Also supports `patchType: JSONPatch`. CEL variables: `object`, `oldObject`, `request`, `params`, `namespaceObject`, `authorizer`.
