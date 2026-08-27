# Upgrades and Support

## Upgrade behavior changes

### Upgrade to 1.17 (`upgrade-1.17`)

- RSA certificates with 3072-bit keys use SHA-384 and 4096-bit keys use
  SHA-512. If rotation fails, verify that every consumer supports the stronger
  signature hash.
- Structured logging adds contextual fields. Update tooling that matches whole
  log lines or literal message strings.
- `ValidateCAA` is deprecated and is removed in 1.18; stop enabling it.

### Upgrade to 1.18 (`upgrade-1.18`)

- `Certificate.spec.privateKey.rotationPolicy` defaults to `Always`, not
  `Never`. Before upgrading, explicitly set `Never` where key reuse is
  required.
- `Certificate.spec.revisionHistoryLimit` defaults to `1`, not an unset value.
  Set the desired history explicitly when one retained revision is insufficient.

### Upgrade to 1.19 (`upgrade-1.19`)

- The ACME request count and duration metrics replaced the high-cardinality
  `path` label with `action`. Rewrite PromQL; use relabeling or a recording rule
  only if old path-level semantics must be preserved.
- From 1.19.6, `cert-manager-edit` no longer permits Challenge creation or
  Order creation, patching, and updates. Certificate-driven issuance is
  unaffected; direct-management tools need dedicated RBAC.

### Upgrade to 1.21 (`upgrade-1.21`)

- The chart no longer creates token-creation RBAC for the controller
  ServiceAccount. Issuers using that account through `serviceAccountRef.name`
  need explicit `Role` and `RoleBinding` objects or a dedicated account.
- Remove `prometheus.servicemonitor.targetPort`,
  `prometheus.servicemonitor.path`, and `prometheus.podmonitor.path` before
  upgrade. Metrics use fixed `/metrics` and `http-metrics`; custom scrapes must
  replace the old `tcp-prometheus-servicemonitor` port name.

## Distribution and patch-level upgrade floors

### OperatorHub packages (`1.17`)

Red Hat OpenShift and community OperatorHub catalogs stop at cert-manager
1.16.5. Installations sourced there need another distribution method for 1.17
or later.

### Known patch-level floors

- Use 1.17.1 or later for Cloudflare DNS-01 after the upstream Cloudflare API
  break, and 1.17.4 or later for correct permitted versus excluded URI name
  constraints.
- Use 1.18.3 or later for unusually large PEM certificates and chains, and
  1.18.5 or later for IPv6 HTTP-01 subjects and public-key mismatch backoff.
- Skip 1.19.0. Its persisted CRD defaults for issuer-reference group and kind
  can cause unnecessary reissuance; 1.19.1 restores runtime defaults and also
  restores trailing-dot DNS SAN support. Use 1.19.2 or later with
  `global.nodeSelector` so common and component selectors merge correctly.
- Use 1.20.1 or later on OpenShift because 1.20.0 omits issuer-finalizer RBAC
  needed by the Order controller. Use 1.20.2 or later when combining
  `webhook.config` with `webhook.volumes`, because earlier charts can render
  invalid YAML. These advisories are from batch `1.20`.
- Upgrade from 1.21.0 to `1.21.1` when using disabled renewal: 1.21.0 can panic
  on `spec.renewal.policy: Disabled`. The patch also lets an ACME DNS-01 issuer
  recover after a previously missing referenced Secret is created instead of
  remaining `InvalidSolver`.

## Support lifecycle (`support-lifecycle`)

### Release window

Each minor is supported at least until the second subsequent minor ships, and
only the newest patch on a supported branch receives fixes. At the recorded
snapshot, 1.21 is supported until 1.23, 1.20 until 1.22, and 1.19 and earlier
are end of life; 1.22 was tentatively planned for November 2026.

### Kubernetes and OpenShift compatibility

| cert-manager | Supported and tested Kubernetes | Supported OpenShift |
|:---:|:---:|:---:|
| 1.21 | 1.33–1.36 | 4.20–4.22 |
| 1.20 | 1.32–1.35 | 4.19–4.21 |

OpenShift support follows the mapped Kubernetes release. Mappings for an
OpenShift version that has not shipped are predictions.

A supported-but-untested Kubernetes release lacks regular end-to-end runs, but
maintainers still respond to and fix reported problems. Versions outside the
supported range are generally neither tested nor fixed.

### Backports and LTS

Security fixes go to both supported branches and trigger patch releases.
Critical regressions and upgrade bugs are also usually backported immediately;
older fixes or changes with runtime risk may be withheld to preserve patch-line
stability.

Upstream provides no LTS branch or post-EOL updates. CyberArk offers a
commercial 1.17 LTS release through February 3, 2027.
