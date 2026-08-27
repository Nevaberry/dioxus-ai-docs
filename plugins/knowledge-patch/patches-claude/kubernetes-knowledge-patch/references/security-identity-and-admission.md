# Security, Identity, and Admission

Use this reference for workload credentials, authentication, authorization,
impersonation, admission policy, Pod security, and identity-related kubelet
integrations.

## ServiceAccount and image credentials

### Prefer bound ServiceAccount tokens (1.33-guide)

Bound tokens carry a unique JTI and node information for audit and validation.
Node-specific restrictions can limit a token to its designated node.

### Constrain kubelet token audiences (1.33.0)

Kubelet token-request configuration can dynamically select ServiceAccount and
audience. Default-on `ServiceAccountNodeAudienceRestriction` makes
NodeRestriction require that the requested audience appear in the Pod's token
volume specification.

### Use workload-bound image credentials (1.33-guide, 1.34-guide)

Kubelet's on-disk image credential provider can request a short-lived,
audience-bound ServiceAccount token tied to the requesting Pod, enabling OIDC
registry authentication without image-pull Secrets.

For a v1 provider using a token, `tokenAttributes.cacheType` is required and
must be `ServiceAccount` or `Token`. The
`--image-credential-provider-config` path may be a directory; kubelet merges
`.json`, `.yaml`, and `.yml` files in lexical order (1.34.0).

### Verify credentials for cached images (1.33-guide, 1.35-guide)

Beta default-on `KubeletEnsureSecretPulledImages` can require authentication
for a new credential set even when `IfNotPresent` or `Never` reuses a cached
private image. Choose the compatibility and enforcement behavior with
`imagePullCredentialsVerificationPolicy`.

### Configure external signing bounds (1.33.0, 1.34-guide)

`--service-account-max-token-expiration` may be combined with
`--service-account-signing-endpoint` only when it does not exceed the external
signer's maximum. Out-of-process `ExternalJWTSigner` is beta and enabled by
default.

### Send CSI tokens through secrets (1.35-guide)

Set `CSIDriver.spec.serviceAccountTokenInSecrets: true` to place tokens in
`NodePublishVolume` secrets instead of the routinely logged `volume_context`.

## X.509 workload and client identity

### Parse a user UID from client certificates (1.33.0)

X.509 authentication reads a user UID from one string-valued subject RDN with
OID `1.3.6.1.4.1.57683.2`. Beta `AllowParsingUserUIDFromCertAuth` can disable
the parsing.

### Avoid overlapping client-CA privilege (1.35.0)

When `--requestheader-client-ca-file` and `--client-ca-file` contain overlapping
certificates, kube-apiserver requires `--requestheader-allowed-names`. This
prevents ordinary client certificates from supplying authenticating-proxy
headers.

### Roll out Pod certificates deliberately (1.34-guide, 1.35-guide)

`PodCertificateRequest` lets kubelet generate keys, request and rotate
certificates, and project bundles into a Pod. Node restrictions protect signer
isolation. Beta use still requires both the feature gate and `v1beta1`
certificate API groups; `PodCertificateProjection.UserAnnotations` reaches the
request as `UnverifiedUserAnnotations` (1.35.0).

The beta API adds `spec.stubPKCS10Request` for CAs that require PKCS#10.
`spec.pkixPublicKey` and `spec.proofOfPossession` are deprecated (1.36.0).

### Project cluster trust bundles (1.33.0)

`ClusterTrustBundleProjection` requires the `ClusterTrustBundle` API at
`v1beta1` plus the kubelet gate. Restart kubelet if the API becomes available
only after kubelet starts.

## Authorization and impersonation

### Require selectors in broad reads (1.34-guide)

Authorizers, including webhooks and the node authorizer, can inspect label and
field selectors for `list`, `watch`, and `deletecollection`. A policy may
require `.spec.nodeName`; omitting a required selector is unauthorized.

### Limit anonymous access by path (1.34-guide)

Use a strict anonymous endpoint allowlist for `/healthz`, `/readyz`, and
`/livez` instead of enabling anonymous authentication globally and relying on
RBAC not to expose other resources.

### Constrain impersonation per operation (1.35-guide, 1.36-guide)

`ConstrainedImpersonation` adds checks such as
`impersonate-on:<mode>:<verb>`, limiting an impersonated identity to selected
actions. The beta transition prefers the new checks while honoring existing
`impersonate` rules so clusters can migrate incrementally.

### Grant create for Pod streaming (1.35.0)

Default-on `AuthorizePodWebsocketUpgradeCreatePermission` requires `create` on
`pods/exec`, `pods/attach`, and `pods/portforward` for WebSocket and SPDY.
Roles granting only `get` no longer authorize WebSocket upgrades.

## Authentication configuration

### Use structured v1 authentication config (1.34.0)

Files passed to `--authentication-config` may use
`apiserver.config.k8s.io/v1`. JWT issuers can set
`issuer.egressSelectorType` to `controlplane` or `cluster`; unset preserves the
old no-selector path. CEL mappings can access escaped or optional keys with
bracket syntax such as `claims[?"kubernetes.io"]`.

## Mutating and unified admission

### Author CEL mutation safely (1.34-guide)

`MutatingAdmissionPolicy` supports server-side-apply `Object{...}`
configurations or arrays of `JSONPatch` operations and requires a
`MutatingAdmissionPolicyBinding`. A binding may use `paramRef`. Apply
configurations cannot modify atomic structs, maps, or arrays; use
`jsonpatch.escapeKey()` for keys containing `/` or `~`.

The beta form was opt-in and required both:

```text
--feature-gates=MutatingAdmissionPolicy=true
--runtime-config=admissionregistration.k8s.io/v1beta1=true
```

### Migrate stored policies before API cleanup (1.34.0, 1.35.0)

Initial beta serving in 1.34 still stored alpha objects, so operators had to run
a storage migration. In 1.35 the stored version became
`admissionregistration.k8s.io/v1beta1`.

### Use the stable admission APIs (1.36.0)

`MutatingAdmissionPolicy` is stable at
`admissionregistration.k8s.io/v1` and enabled by default. The `v1alpha1`
`WebhookAdmissionConfiguration` is removed; webhook config files must use
`apiserver.config.k8s.io/v1`.

Alpha manifest-based admission configuration can place plugins and their
settings in one structured, versioned manifest instead of scattering them
across flags and separate files (1.36-guide).

## Pod security and runtime identity

### Use strict supplemental groups (1.33-guide, 1.35-guide)

The `SupplementalGroupsPolicy` feature adds
`spec.securityContext.supplementalGroupsPolicy: Strict`, which uses only
explicitly configured groups;
`Merge` also imports memberships from image `/etc/group`. Stable Strict support
requires containerd 2.0 or newer or CRI-O 1.31 or newer and is advertised at
`Node.status.features.supplementalGroupsPolicy`.

Kubelet reports the initially attached UID, GID, and groups in
`status.containerStatuses[*].user.linux`; a privileged process may change them
later.

### Leave probe hosts unset (1.34-guide)

Restricted Pod Security rejects HTTP probes and lifecycle handlers with an
explicit remote `host`. Leave `host` unset so kubelet targets the Pod IP.

### Read structured AppArmor fields (1.34.0)

Profiles set through Pod or container `securityContext` are no longer copied to
`container.apparmor.security.beta.kubernetes.io/*` annotations. Consumers must
inspect the structured security context.
