# Image Verification and HTTP Security

## Dedicated image verification

`ImageValidatingPolicy` separates image verification into its own CEL-first
policy kind (since 1.14.0). It can:

- Select image references with globs or CEL.
- Verify signatures and attestations such as SBOMs.
- Extract images from arbitrary JSON payloads.
- Supply certificates dynamically through CEL.

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
    - expression: images.containers.map(image, verifyImageSignatures(image, [attestors.notary])).all(e, e > 0)
      message: failed to verify image with notary cert
```

Use `NamespacedImageValidatingPolicy` when policy ownership and effects must be
limited to its containing namespace. The namespaced kind is available from
1.16.0.

Image verification supports Cosign v3 features as of 1.17.0.

## Legacy registry credentials

For image verification in `ClusterPolicy`,
`imageRegistryCredentials.secrets` accepts cross-namespace references in
`namespace/name` form (since 1.18.0):

```yaml
imageRegistryCredentials:
  secrets:
    - tenant-a/registry-credentials
```

Kyverno also automatically uses a Pod's `imagePullSecrets` as registry
credentials. This lets namespaces manage access to their own private
registries.

## Harden outbound HTTP calls

HTTP calls from policies have configurable address allowlists and blocklists
(since 1.18.0). Unsafe destinations, including loopback and metadata services,
are blocked by default.

Namespaced policies have HTTP calls disabled by default. Enable them only
through explicit configuration flags after defining the allowed destinations.
Outbound calls use a separate scoped token rather than a token capable of
impersonating Kyverno controllers.

These controls apply to expressions using HTTP facilities such as:

```cel
http.Send("GET", "https://api.example.com/data", {}).body
http.Post(
  "https://audit.api/log",
  {"kind": object.kind},
  {"Content-Type": "application/json"}
).logged == true
```

Before enabling policy HTTP:

1. Decide whether the policy needs external data at admission time.
2. Define a narrow address allowlist.
3. Keep loopback and metadata endpoints blocked.
4. Enable calls explicitly for namespaced policies.
5. Test failure behavior when the remote endpoint is unavailable.
