# Image Verification

## Dedicated Image Policy

`ImageValidatingPolicy` separates image verification into
`policies.kyverno.io/v1alpha1` in 1.14.0. Use the API version served by the
target cluster; the family moved to `v1beta1` in 1.16.0 and stable `v1` in
1.17.0.

The policy can:

- select image references with globs or CEL;
- verify signatures and attestations, including SBOMs;
- extract images from arbitrary JSON payloads rather than only Pod-shaped
  resources;
- obtain certificates dynamically through CEL;
- inspect OCI registry metadata with CEL.

Example with a certificate loaded from a ConfigMap:

```yaml
apiVersion: policies.kyverno.io/v1
kind: ImageValidatingPolicy
metadata:
  name: check-images
spec:
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: [v1]
        operations: [CREATE]
        resources: [pods]
  variables:
    - name: cm
      expression: resource.Get("v1", "configmaps", object.metadata.namespace, "keys")
  matchImageReferences:
    - glob: ghcr.io/*
  attestors:
    - name: notary
      notary:
        certs:
          expression: variables.cm.data.certificate
  validations:
    - expression: images.containers.map(
        image,
        verifyImageSignatures(image, [attestors.notary])
      ).all(e, e > 0)
      message: failed to verify image with notary cert
```

Grant only the resource-read permissions needed by dynamic certificate lookup.
Offline testing must supply or emulate the external resource data.

## Namespaced Verification

`NamespacedImageValidatingPolicy` arrived in 1.16.0. It mirrors
`ImageValidatingPolicy` but applies only in its own namespace, enabling
team-owned enforcement and narrower RBAC. Kyverno 1.18.0 disables HTTP calls
from namespaced policies by default, so any HTTP-dependent verification must be
explicitly enabled and restricted.

## Exception-Provided Images

Since 1.16.0, `PolicyException.spec.images` may carry allowed image patterns.
A referenced policy reads them through `exceptions.allowedImages`, allowing
the policy to bypass verification only for a listed image rather than exempting
the entire workload.

```cel
string(container.image) in exceptions.allowedImages
```

Combine this with `policyRefs` and narrow CEL `matchConditions`. Decide whether
the matching exception should report the default `skip` or set
`spec.reportResult: pass`.

## Cosign Compatibility

Image verification supports Cosign v3 features as of 1.17.0, maintaining
compatibility with the evolving Sigstore ecosystem. Test existing attestors and
verification material when upgrading Cosign-dependent workflows.

## Legacy ClusterPolicy Registry Credentials

For legacy `ClusterPolicy` image verification in 1.18.0,
`imageRegistryCredentials.secrets` accepts cross-namespace Secret references in
`namespace/name` form:

```yaml
imageRegistryCredentials:
  secrets:
    - tenant-a/registry-credentials
```

Kyverno also automatically uses a Pod's `imagePullSecrets` as registry
credentials. This allows each namespace to manage access to its own private
registries. Preserve least privilege when Kyverno reads cross-namespace
Secrets.

## CLI and Reports

Since 1.14.0, the CLI can evaluate `ImageValidatingPolicy` against arbitrary
JSON payloads, such as a Dockerfile represented as JSON. This permits
pre-cluster verification of images extracted from non-Kubernetes payloads.

Generated `PolicyReport` results identify the producing policy type, for
example `source: KyvernoImageValidatingPolicy`, and link results to evaluated
resources through owner references.
