# Security, Identity, and Admission

## ServiceAccount and registry credentials

### Bound ServiceAccount tokens carry stronger identity (1.33-guide)

Bound tokens have a unique JTI and node identity for validation/auditing and may
be restricted to their designated node.

### Image-pull authentication covers cached images and ServiceAccounts (1.33-guide)

The alpha cached-image mode can require an authentication check for each new
credential set even when `IfNotPresent` or `Never` reuses local data. Separately,
the on-disk credential provider may request a ServiceAccount token for
OIDC-backed registry access without pull Secrets.

### Kubelet token requests are audience constrained (1.33.0)

Kubelet token-request configuration can dynamically select ServiceAccount and
audience. Default-on `ServiceAccountNodeAudienceRestriction` makes
NodeRestriction require the requested audience in the Pod token-volume spec.

### External ServiceAccount signers accept a bounded maximum (1.33.0)

`--service-account-max-token-expiration` works with
`--service-account-signing-endpoint` if it does not exceed the external signer's
maximum.

### Cluster trust bundles move to `v1beta1` (1.33.0)

`ClusterTrustBundleProjection` requires the `ClusterTrustBundle` API at
`v1beta1` and the kubelet feature gate. If the API becomes available only after
kubelet starts, restart kubelet to activate projection support.

### ServiceAccount token integrations advance to beta (1.34-guide)

Image credential providers can use short-lived, audience-bound tokens tied to
the requesting Pod. Out-of-process `ExternalJWTSigner` is beta and default-on.

### Image credential provider configuration is composable (1.34.0)

For a v1 provider using ServiceAccount tokens, `tokenAttributes.cacheType` is
required and is `ServiceAccount` or `Token`.
`--image-credential-provider-config` may point to a directory whose JSON/YAML
files merge in lexicographic order.

### Cached-image credential checks are default-on (1.35-guide)

Default-on beta `KubeletEnsureSecretPulledImages` verifies credentials for
cached private images. Choose compatibility or enforcement with
`imagePullCredentialsVerificationPolicy`.

### CSI tokens can use the secrets channel (1.35-guide)

Set `CSIDriver.spec.serviceAccountTokenInSecrets: true` to deliver tokens in
`NodePublishVolume` secrets rather than routinely logged `volume_context`.

## Authentication and authorization

### Client certificates can carry a user UID (1.33.0)

X.509 authentication reads a user UID from one string RDN with OID
`1.3.6.1.4.1.57683.2`. Beta `AllowParsingUserUIDFromCertAuth` can disable it.

### Structured authentication configuration reaches v1 (1.34.0)

`--authentication-config` accepts `apiserver.config.k8s.io/v1`. A JWT issuer may
select `controlplane` or `cluster` egress with `issuer.egressSelectorType`;
unset retains no selector. CEL accesses escaped or optional names with syntax
such as `claims[?"kubernetes.io"]`.

### Authorizers can enforce request selectors (1.34-guide)

Authorizers, including webhooks and the node authorizer, can inspect label and
field selectors on `list`, `watch`, and `deletecollection`. A policy may require
`.spec.nodeName`; omitting a required selector makes the request unauthorized.

### Anonymous authentication can be limited by path (1.34-guide)

Use an exact endpoint allowlist for unauthenticated `/healthz`, `/readyz`, and
`/livez` rather than global anonymous access that can combine with accidental
RBAC grants.

### Impersonation can be constrained per operation (1.35-guide)

Alpha `ConstrainedImpersonation` performs a second authorization check with
verbs like `impersonate-on:<mode>:<verb>`, limiting an impersonated identity to
particular operations.

### Constrained impersonation has a compatible beta transition (1.36-guide)

The server prefers constrained checks but honors existing `impersonate` RBAC,
allowing incremental adoption.

### WebSocket Pod streaming requires `create` authorization (1.35.0)

With default-on `AuthorizePodWebsocketUpgradeCreatePermission`, WebSocket and
SPDY requests for `pods/exec`, `pods/attach`, and `pods/portforward` need
`create`. Update roles that granted only `get`.

### Fine-grained kubelet API authorization is stable (1.36-guide)

`KubeletFineGrainedAuthz` allows monitoring clients narrow kubelet HTTPS API
permissions rather than broad `nodes/proxy` access.

### Overlapping client CAs require an allowed-name restriction (1.35.0)

If `--requestheader-client-ca-file` and `--client-ca-file` overlap, set
`--requestheader-allowed-names` so ordinary client certs cannot inject proxy
authentication headers.

## Workload identity and Pod security

### Supplemental group membership can be strict (1.33-guide)

Default-on beta `SupplementalGroupsPolicy` adds
`spec.securityContext.supplementalGroupsPolicy: Strict`, using only explicit
groups. `Merge` also imports image `/etc/group` memberships.

### Restricted Pod security rejects remote probe hosts (1.34-guide)

HTTP probes and lifecycle handlers with explicit `host` fail Restricted Pod
Security. Leave it unset so kubelet targets the Pod IP.

### AppArmor annotations are no longer synthesized (1.34.0)

Profiles in Pod/container security context are not copied to legacy
`container.apparmor.security.beta.kubernetes.io/*` annotations. Read structured
fields.

### Pods can obtain kubelet-managed X.509 identities (1.34-guide)

Alpha `PodCertificateRequest` lets kubelet request and manage workload
certificates for mTLS rather than relying on bearer tokens.

### Pod certificates advance to beta (1.35-guide)

Kubelet generates keys, requests and rotates certificates, and writes credential
bundles to the Pod filesystem. API-server node restrictions isolate signers.

### Pod certificates remain opt-in at beta (1.35.0)

Enable both the feature and `v1beta1` certificates API groups.
`PodCertificateProjection.UserAnnotations` reaches requests as
`UnverifiedUserAnnotations`.

### Pod certificates prefer stub PKCS#10 requests (1.36.0)

Use `spec.stubPKCS10Request` for CAs requiring PKCS#10.
`spec.pkixPublicKey` and `spec.proofOfPossession` are deprecated.

## Mutating admission and policy

### Mutating admission policies are beta but opt-in (1.34-guide)

`admissionregistration.k8s.io/v1beta1` uses CEL server-side-apply `Object{...}`
or arrays of JSON Patch operations. A binding is required and may provide
`paramRef`. Enable both the feature gate and runtime API. Apply configurations
cannot change atomic structs, maps, or arrays; use `jsonpatch.escapeKey()` for
JSON Pointer keys containing `/` or `~`.

### Beta mutating policies still need storage migration (1.34.0)

Enabling the beta API does not change the initial alpha stored version; run a
storage migration rather than leaving alpha data in etcd.

### MutatingAdmissionPolicy storage moves to `v1beta1` (1.35.0)

The stored version becomes `v1beta1`, replacing the earlier alpha storage
behavior.

### Admission configuration APIs graduate and retire (1.36.0)

`MutatingAdmissionPolicy` is stable as `admissionregistration.k8s.io/v1` and
default-on. `v1alpha1` `WebhookAdmissionConfiguration` is removed; webhook
configuration files use `apiserver.config.k8s.io/v1`.
