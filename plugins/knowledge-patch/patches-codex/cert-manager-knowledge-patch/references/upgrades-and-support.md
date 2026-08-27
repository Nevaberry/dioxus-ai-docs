# Upgrades and Support

## Pre-upgrade removals and defaults

### Stop enabling ValidateCAA `(upgrade-1.17)`

The `ValidateCAA` feature gate is deprecated for removal in 1.18. Remove manual enablement before upgrading.

### Private-key rotation and history `(upgrade-1.18)`

`Certificate.spec.privateKey.rotationPolicy` defaults to `Always` rather than `Never`; explicitly set `Never` before upgrading Certificates that must retain old behavior. `Certificate.spec.revisionHistoryLimit` defaults to `1` rather than `nil`.

### Direct ACME object RBAC `(upgrade-1.19)`

From 1.19.6, `cert-manager-edit` no longer allows creating Challenges or creating, patching, or updating Orders. Ordinary Certificate-driven issuance is unaffected; direct-resource tooling needs explicit permissions.

### Controller ServiceAccount token RBAC `(upgrade-1.21)`

The Helm chart stops creating the controller ServiceAccount's token-creation Role and RoleBinding. Add explicit RBAC or use a dedicated ServiceAccount before upgrading any issuer whose `serviceAccountRef.name` points to the controller account.

### Prometheus override cleanup `(upgrade-1.21)`

Delete `prometheus.servicemonitor.targetPort`, `prometheus.servicemonitor.path`, and `prometheus.podmonitor.path`; otherwise Helm schema validation fails. Replace custom uses of port name `tcp-prometheus-servicemonitor` with `http-metrics` and use fixed path `/metrics`.

## Corrective patch releases

### 1.17 line `(1.17)`

- Require 1.17.1+ for Cloudflare DNS-01 after the upstream API break.
- Require 1.17.4+ for URI name constraints; earlier releases copied permitted URI domains into excluded URI domains.
- ACME authorization uses a two-minute timeout from 1.17.3.

### 1.18 line `(1.18)`

- Require 1.18.1+ to set `ACMEHTTP01IngressPathTypeExact: false` when exact solver paths conflict with ingress-nginx.
- Do not rely on `global.rbac.disableHTTPChallengesRole`; it was added in 1.18.0 and removed in 1.18.2.
- Larger PEM chains are handled from 1.18.3.
- IPv6 HTTP-01 Host headers and mismatched-CSR-key backoff are corrected from 1.18.5.

### 1.19 line `(1.19)`

Avoid 1.19.0. Version 1.19.1 reverts persisted CRD defaults for issuer-reference group and kind, preventing unnecessary reissuance, and restores trailing-dot DNS SANs. Use 1.19.2+ for correct merging of `global.nodeSelector` with component selectors.

### 1.20 line `(1.20)`

- Use 1.20.1+ when inferred Gateway `parentRefs` interact with annotation overrides; 1.20.0 can duplicate references.
- Use 1.20.1+ on OpenShift because 1.20.0 lacks issuer-finalizer RBAC required by the Order controller.
- Use 1.20.2+ when setting both `webhook.config` and `webhook.volumes`; earlier releases can render invalid Helm YAML.

### 1.21 line `(1.21)` `(1.21.1)`

Version 1.21.1 fixes a controller panic caused by `spec.renewal.policy: Disabled` in 1.21.0. It also lets DNS-01 issuers recover after a previously missing solver Secret is created; 1.21.0 can remain stuck at `InvalidSolver`.

## Feature-gate progression

### Name constraints and finalizers `(1.17)`

`NameConstraints` and `UseDomainQualifiedFinalizer` are beta and enabled by default. The former enables CA certificate name constraints; the latter avoids warnings with a domain-qualified finalizer.

### Additional outputs `(1.18)`

`AdditionalCertificateOutputFormats` is GA, so remove its feature-gate configuration.

### CA injection `(1.17)` `(1.19)` `(1.21)`

`CAInjectorMerging` began as opt-in, became beta and enabled by default, and is now GA and unconditional. Replacement semantics cannot be restored with the old gate. Cainjector always uses server-side apply, making `ServerSideApply` deprecated.

### OtherNames and rotation `(1.20)`

`OtherNames` is beta and enabled by default. `DefaultPrivateKeyRotationPolicyAlways` is GA and cannot be disabled; set a Certificate's rotation policy explicitly instead.

### Gateway configuration `(1.21)`

Controller fields `enableGatewayAPI` and `enableGatewayAPIListenerSet` are deprecated in favor of `gatewayAPI.enabled` and `gatewayAPI.enableListenerSet`. The old fields still work during migration.

## Distribution and support policy

### OperatorHub ending `(1.17)`

OperatorHub catalogs end at 1.16.5. Choose another distribution path for newer cert-manager releases.

### Release-driven support window `(support-lifecycle)`

Each minor is supported at least until the second subsequent minor ships, and only the latest patch of each supported minor receives support. At the lifecycle snapshot, 1.21 remains supported until 1.23 and 1.20 until 1.22; 1.19 and earlier are EOL. Release 1.22 was tentatively planned for November 2026.

### Kubernetes and OpenShift compatibility `(support-lifecycle)`

| cert-manager | Supported and tested Kubernetes | Supported OpenShift |
|:---:|:---:|:---:|
| 1.21 | 1.33–1.36 | 4.20–4.22 |
| 1.20 | 1.32–1.35 | 4.19–4.21 |

OpenShift support follows the release's mapped Kubernetes version. Mappings for OpenShift releases that do not yet exist may be predictions.

### Supported versus tested `(support-lifecycle)`

A supported-but-untested Kubernetes version does not receive regular end-to-end runs, but maintainers respond to and fix reported issues. Versions outside the supported range are generally neither tested nor fixed.

### Backport policy `(support-lifecycle)`

Security issues are backported to both supported releases and immediately trigger a patch. Critical regressions and upgrade bugs are usually backported promptly. Long-standing fixes or changes with runtime risk may be withheld from patch branches to protect stability.

### No upstream LTS `(support-lifecycle)`

The cert-manager maintainers do not provide LTS releases or updates after EOL. CyberArk offers a commercial 1.17 LTS through February 3, 2027.
