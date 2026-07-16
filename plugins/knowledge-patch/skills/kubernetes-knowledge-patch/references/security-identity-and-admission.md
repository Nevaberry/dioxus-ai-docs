# Security, Identity, and Admission

Use this reference for authentication, authorization, ServiceAccounts, workload identity, Pod security, admission, impersonation, and audit policy.

Entries are grouped by task; the parenthetical identifier is the source batch.

## Admission configuration APIs graduate and retire (1.36.0)

`MutatingAdmissionPolicy` is stable as `admissionregistration.k8s.io/v1` and enabled by default. The `v1alpha1` `WebhookAdmissionConfiguration` is removed; admission webhook configuration files must use `apiserver.config.k8s.io/v1`.

## Admission control can use a unified manifest (1.36-guide)

Alpha manifest-based admission configuration puts admission plugins and their settings into one structured, versioned manifest instead of distributing configuration across component flags and separate plugin files.

## Anonymous authentication can be limited by path (1.34-guide)

Anonymous access can now use a strict endpoint allowlist instead of being globally on or off, allowing unauthenticated health endpoints such as `/healthz`, `/readyz`, and `/livez` without exposing other paths through accidental RBAC grants.

## AppArmor annotations are no longer synthesized (1.34.0)

AppArmor profiles set through Pod or container `securityContext` are no longer copied to `container.apparmor.security.beta.kubernetes.io/*` annotations; consumers must inspect the structured security-context fields.

## Audit policy and retention semantics changed (1.36.0)

Audit resource rules can use `group: "*"` to match every API group. Setting `--audit-log-maxsize=0` now disables rotation; the defaults are `--audit-log-maxage=366` and `--audit-log-maxbackup=100`, and both pruning controls must be set explicitly to `0` to retain every rotated log.

## Authorizers can enforce request selectors (1.34-guide)

Authorizers, including authorization webhooks and the node authorizer, can evaluate label and field selectors on `list`, `watch`, and `deletecollection` requests. A policy can therefore require a selector such as `.spec.nodeName`; omitting the required selector makes the request unauthorized.

## Beta mutating policies still need storage migration (1.34.0)

Enabling `admissionregistration.k8s.io/v1beta1` MutatingAdmissionPolicy in 1.34 does not change the default stored version from alpha, so operators using the beta API must run a storage migration rather than leave alpha data in etcd.

## Bound ServiceAccount tokens carry stronger identity (1.33-guide)

The stable bound-token improvements add a unique JTI and node information for validation and auditing, and allow node-specific restrictions so a token can be limited to its designated node.

## Cached-image credential checks are default-on (1.35-guide)

`KubeletEnsureSecretPulledImages` is beta and enabled by default, so locally cached private images are subject to credential verification. Operators can choose the compatibility-versus-enforcement policy with `imagePullCredentialsVerificationPolicy`.

## Client certificates can carry a user UID (1.33.0)

Components accepting X.509 client authentication now read the user UID from a single string-valued subject RDN with OID `1.3.6.1.4.1.57683.2`; the beta `AllowParsingUserUIDFromCertAuth` gate can disable parsing.

## Cluster trust bundles move to `v1beta1` (1.33.0)

`ClusterTrustBundleProjection` now requires the `ClusterTrustBundle` API at `v1beta1` plus its kubelet feature gate; if that API becomes available only after kubelet starts, restart kubelet to activate projection support.

## Constrained impersonation has a compatible beta transition (1.36-guide)

The API server prefers the new constrained authorization checks, but existing `impersonate` RBAC rules continue to work, allowing clusters to adopt per-operation impersonation permissions incrementally.

## External ServiceAccount signers accept a bounded maximum (1.33.0)

`--service-account-max-token-expiration` can now be combined with `--service-account-signing-endpoint`, provided the configured maximum does not exceed the external signer's own maximum expiration.

## Fine-grained kubelet API authorization is stable (1.36-guide)

`KubeletFineGrainedAuthz` is GA, allowing monitoring and observability clients to receive narrow permissions for the kubelet HTTPS API instead of the overly broad `nodes/proxy` permission.

## Host-network Pods can use user namespaces (1.35.0)

The alpha, default-off `UserNamespacesHostNetworkSupport` gate permits Pods to combine `hostNetwork` with a user namespace.

## Image credential provider configuration is composable (1.34.0)

For a v1 provider using a ServiceAccount token, `tokenAttributes.cacheType` is required and must be `ServiceAccount` or `Token`. `--image-credential-provider-config` can now point to a directory whose `.json`, `.yaml`, and `.yml` files are merged in lexicographic order.

## Image-pull authentication covers cached images and ServiceAccounts (1.33-guide)

An alpha security mode can require an authentication check for each new credential set even when `IfNotPresent` or `Never` reuses an image already on the node. Separately, kubelet's on-disk credential provider can request an optional ServiceAccount token, enabling OIDC-backed registry authentication without image-pull Secrets.

## Impersonation can be constrained per operation (1.35-guide)

With the alpha `ConstrainedImpersonation` gate, authorization performs a second check using verbs such as `impersonate-on:<mode>:<verb>`, allowing an impersonated identity to be limited to particular actions instead of receiving all of that identity's powers.

## Kubelet token requests are audience constrained (1.33.0)

Kubelet token-request configuration can dynamically select the ServiceAccount name and audience, and the default-on `ServiceAccountNodeAudienceRestriction` gate makes NodeRestriction require that requested audience to appear in the Pod's token volume specification.

## Mutating admission policies are beta but opt-in (1.34-guide)

`admissionregistration.k8s.io/v1beta1` policies provide in-process CEL mutation with either server-side-apply `Object{...}` configurations or arrays of `JSONPatch` operations; a `MutatingAdmissionPolicyBinding` is required and can supply a parameter resource through `paramRef`. The beta feature is off by default and requires both controls:

```text
--feature-gates=MutatingAdmissionPolicy=true
--runtime-config=admissionregistration.k8s.io/v1beta1=true
```

Apply configurations cannot modify atomic structs, maps, or arrays; JSON Patch expressions should use `jsonpatch.escapeKey()` for path keys containing `/` or `~`.

## MutatingAdmissionPolicy storage moves to `v1beta1` (1.35.0)

The storage version for MutatingAdmissionPolicy is now `v1beta1`, replacing the alpha storage-version behavior present when the beta API first appeared.

## Overlapping client CAs require an allowed-name restriction (1.35.0)

When `--requestheader-client-ca-file` and `--client-ca-file` contain overlapping certificates, kube-apiserver now requires `--requestheader-allowed-names` so ordinary client certificates cannot supply authenticating-proxy headers.

## Pod certificates advance to beta (1.35-guide)

`PodCertificateRequest` now lets kubelet generate keys, request and rotate certificates, and write credential bundles directly into a Pod's filesystem. API-server node restrictions protect signer isolation, so certificate issuance can avoid bearer tokens.

## Pod certificates prefer stub PKCS#10 requests (1.36.0)

The beta Pod Certificates API adds `spec.stubPKCS10Request` for certificate authorities that require a PKCS#10 request; `spec.pkixPublicKey` and `spec.proofOfPossession` are deprecated.

## Pod certificates remain opt-in at beta (1.35.0)

Using PodCertificateRequest still requires enabling both its feature gate and the `v1beta1` certificates API groups. PodCertificateProjection also gains `UserAnnotations`, which reaches requests as `UnverifiedUserAnnotations`.

## Pod user namespaces are beta and enabled by default (1.33-guide)

Linux Pods still opt in with `spec.hostUsers: false`; support requires an appropriate runtime (containerd 2.0 or newer, or CRI-O) and idmapped-mount support for the root filesystem and every volume filesystem. NFS is unsupported, and tmpfs-backed Secret, ConfigMap, projected, and downward-API volumes require Linux 6.3; the feature maps container root to an unprivileged, non-overlapping host ID range.

```yaml
spec:
  hostUsers: false
```

## Pods can obtain kubelet-managed X.509 identities (1.34-guide)

The alpha `PodCertificateRequest` mechanism lets kubelet request and manage workload certificates for mTLS to the API server or other certificate-aware services, rather than requiring bearer-token identity.

## Restricted Pod security rejects remote probe hosts (1.34-guide)

HTTP probes and lifecycle handlers with an explicitly set `host` no longer satisfy the Restricted Pod Security Standard; leave `host` unset so kubelet targets the Pod IP.

## ServiceAccount token integrations advance to beta (1.34-guide)

Kubelet image credential providers can use short-lived, audience-bound tokens tied to the requesting Pod, and out-of-process `ExternalJWTSigner` ServiceAccount token signing is now beta and enabled by default.

## Strict supplemental groups expose support and identity (1.35-guide)

At GA, `supplementalGroupsPolicy: Strict` requires containerd 2.0 or newer or CRI-O 1.31 or newer; support is advertised at `Node.status.features.supplementalGroupsPolicy`. Kubelet reports the initially attached UID, GID, and groups in `status.containerStatuses[*].user.linux`, but a privileged process can change that identity later.

## Structured authentication configuration reaches v1 (1.34.0)

Files passed through `--authentication-config` can use `apiserver.config.k8s.io/v1`, and a JWT issuer can select `controlplane` or `cluster` egress with `issuer.egressSelectorType`; leaving it unset preserves the previous no-selector behavior. CEL mappings can access escaped or optional names with bracket syntax such as `claims[?"kubernetes.io"]`.

## Supplemental group membership can be strict (1.33-guide)

The default-on beta `SupplementalGroupsPolicy` feature adds `spec.securityContext.supplementalGroupsPolicy: Strict`, which uses only explicitly configured groups; the backward-compatible `Merge` policy also imports memberships from the image's `/etc/group`.

## User-namespaced Pods cannot use block devices (1.34.0)

Pods with `hostUsers: false` are rejected if they also declare `volumeDevices`.

## WebSocket Pod streaming requires `create` authorization (1.35.0)

With the default-on `AuthorizePodWebsocketUpgradeCreatePermission` gate, `pods/exec`, `pods/attach`, and `pods/portforward` require `create` for both WebSocket and SPDY requests. Update custom Roles and ClusterRoles that granted only `get` for WebSocket access.

