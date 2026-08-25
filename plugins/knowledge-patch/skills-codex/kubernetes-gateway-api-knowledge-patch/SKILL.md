---
name: kubernetes-gateway-api-knowledge-patch
description: Kubernetes Gateway API
version: 1.6.0
license: MIT
metadata:
  author: Nevaberry
---


# Kubernetes Gateway API Knowledge Patch

Use this skill when installing or upgrading Gateway API CRDs, authoring
Gateway and Route manifests, implementing a controller, or checking
conformance and status behavior. Start with the upgrade hazards, then open the
reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [API lifecycle and upgrades](references/api-lifecycle-and-upgrades.md) | Safe-upgrade admission, channel identities, CRD graduation, route API migration, ReferenceGrant |
| [Gateways, listeners, and TLS](references/gateways-listeners-and-tls.md) | Addresses, infrastructure, ListenerSet, connection coalescing, client certificates, listener status |
| [Routes, filters, and attachment](references/routes-filters-and-attachment.md) | Route validation, mirroring, CORS, authentication, retries, default Gateways, portability |
| [Policies, status, and conformance](references/policies-status-and-conformance.md) | Backend TLS, session persistence, retry budgets, feature reporting, Mesh capabilities |

## Breaking changes and upgrade blockers

### Respect the safe-upgrade admission policy

Gateway API installs `safe-upgrades.gateway.networking.k8s.io` as a
`ValidatingAdmissionPolicy`. It blocks unsafe CRD combinations and release
downgrades, including:

- adding Experimental CRDs after Standard CRDs are installed;
- downgrading to a release before the policy's supported floor;
- installing monthly Gateway API releases or older releases.

Upgrading Experimental CRDs already present is still allowed. Delete the
policy only for a deliberately guarded operation whose consequences have been
assessed.

### Migrate graduated route and grant APIs

- Write `TLSRoute`, `TCPRoute`, and `UDPRoute` with
  `gateway.networking.k8s.io/v1`.
- Treat the older TLSRoute alpha versions and the `v1alpha2` TCPRoute and
  UDPRoute versions as deprecated.
- Do not expect the Experimental channel to ship `TLSRoute` `v1alpha2`.
- Use `ReferenceGrant` at `v1` and always include `spec`.
- Account for the Kubernetes version requirement imposed by stable
  TLSRoute CEL validation.

Experimental resources have distinct identities. New experimental kinds use
an `X` prefix and `gateway.networking.x-k8s.io`; graduation requires object
recreation under the Standard kind and group. Do not assume an experimental
object changes identity in place.

### Remove retired experimental forms and fields

- Replace `XListenerSet` with the Standard `ListenerSet`; the X-prefixed kind
  is no longer shipped.
- Remove `idleTimeout` from Experimental SessionPersistence configuration.
- Do not configure `TCPRoute` on a TLS listener.
- Do not emit an HTTPRoute without at least one rule.
- Do not emit GRPCRoute or ReferenceGrant objects without `spec`.

### Update validation assumptions

Schema and CEL validation now reject several shapes that older tooling may
have emitted:

- duplicate values in `retry.codes`;
- retry `attempts` values below 1;
- more than one CORS filter in one HTTPRoute rule;
- unsupported host values in CORS origins;
- session `cookieConfig` without persistence type `Cookie`;
- Gateway infrastructure with more than 16 annotations.

Generated clients must model CORS `allowCredentials` as a Boolean that may be
either `true` or `false`, rather than using the earlier enum representation.

## Gateway and listener quick reference

### Handle overlapping TLS configuration

When HTTPS listener configuration overlaps in a way that makes connection
coalescing unsafe, expose `OverlappingTLSConfig` as appropriate. Apply the
clarified Hostname and SNI matching rules and return HTTP 421 for affected
requests.

Client-certificate validation on a TLS-terminating Gateway and selection of
the Gateway client certificate for backend TLS are Standard features. Keep
those concerns distinct from BackendTLSPolicy server validation.

### Handle implementation-assigned addresses

`Gateway.spec.addresses` contains `GatewaySpecAddress` entries whose `value`
may be absent. With the Standard `GatewayEmptyAddress` feature:

- a supporting implementation assigns the address; or
- a non-supporting implementation reports `Programmed=False` with
  `AddressNotAssigned`.

For a missing, unsupported, or malformed infrastructure reference, set
`Accepted` with reason `InvalidParameters`. `GatewayInfrastructure` is a
Standard feature.

### Use ListenerSet status precisely

ListenerSet allows listeners to be merged into a Gateway and can attach
across namespaces. Its listener `port` is required. The obsolete `None`
option for Route namespaces must not be accepted.

Gateway status reports successfully attached sets with
`AttachedListenerSets`. A ListenerSet that cannot be programmed because its
listeners are invalid can report `ListenersNotValid`.

A listener that is not conflicted need not report `Conflicted=False`; absence
of that negative condition is valid.

## Route and filter quick reference

### Validate route structure

- GRPCRoute allows up to 64 matches and requires a top-level `spec`.
- HTTPRoute requires at least one item in `spec.rules`.
- TLSRoute can scale to 4096 hostnames and 4096 rules, but large objects need
  representative API server, etcd, and controller testing.
- TCPRoute and UDPRoute have stable APIs and corresponding conformance
  coverage.

HTTPRoute and GRPCRoute on the same hostname are implementation-dependent:
an implementation may allow or reject the combination. Avoid relying on
coexistence in portable manifests.

### Mirror only the desired traffic

`RequestMirror` can select a percentage of HTTPRoute or GRPCRoute requests.
This is Standard-channel behavior at the Extended support level. For
HTTPRoute, implementations advertise percentage mirroring with
`HTTPRouteRequestPercentageMirror` in
`GatewayClass.status.supportedFeatures`.

### Configure CORS carefully

The HTTPRoute `CORS` filter supports Boolean `allowCredentials`, including
`false`. Do not combine `*` with other entries in `allowMethods`, and do not
place more than one CORS filter in a rule. Standard CORS validation rejects
unsupported values in the host portion of an origin.

### Name and authenticate routes

HTTPRoute rules and matches can carry explicit `name` values, enabling
individual identification. Experimental HTTPRoute external authentication
delegates authorization to an external service; experimental authentication
can also be configured at Gateway scope.

Default-Gateway attachment can cause selected Gateways to program routes
without an ordinary explicit attachment. Both controller implementations and
route owners must account for this additional path.

## Policy and conformance quick reference

### Apply BackendTLSPolicy validation rules

`BackendTLSPolicy` is Standard and uses `ResolvedRefs` for reference
resolution. Follow the standardized invalid-policy and target-reference
conflict behavior.

`subjectAltNames` is Extended and therefore optional for implementations.
When SAN validation is configured, it takes precedence over Hostname
validation. Target references receive CEL validation.

The policy supports implementation-specific
`wellKnownCACertificates` values, additional Route combinations, and up to 16
certificate-authority references.

### Keep experimental retry and persistence fields current

`XBackendTrafficPolicy` replaces `BackendLBPolicy`. It combines session
persistence with destination-wide retry budgets. Nest retry budget values
under `budget.percent` and `budget.interval`; do not use the former flat field
names.

Session-persistence `cookieConfig` is valid only with persistence type
`Cookie`, and the Experimental SessionPersistence API no longer has
`idleTimeout`.

### Discover support instead of assuming it

`GatewayClass.status.supportedFeatures` is the Standard capability-reporting
surface. Percentage request mirroring has a feature name, while experimental
ListenerSet and backend traffic policy forms may require implementation-level
support checks without a conformance feature name.

Mesh-wide experimental configuration reports mesh capabilities separately
from Gateway capabilities. Do not infer one capability set from the other.

## Review workflow

Before applying manifests or shipping controller changes:

1. Identify whether every resource is Standard or Experimental and use its
   correct API identity.
2. Check the installed CRD schema and the safe-upgrade policy before changing
   channels or release families.
3. Validate newly required fields, list bounds, filter uniqueness, and policy
   field relationships.
4. Inspect `GatewayClass.status.supportedFeatures` and implementation
   documentation for Extended or experimental behavior.
5. Verify attachment and programming through status, including negative
   reasons, rather than assuming that admission implies successful
   programming.
6. Exercise TLS coalescing, route-hostname portability, and large-object
   behavior when those edge cases apply.
