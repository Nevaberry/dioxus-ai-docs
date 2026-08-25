---
name: kubernetes-gateway-api-knowledge-patch
description: Kubernetes Gateway API
version: 1.6.0
license: MIT
metadata:
  author: Nevaberry
---



# Kubernetes Gateway API Knowledge Patch

Load this skill when installing or upgrading Gateway API CRDs, writing Gateway
or Route manifests, implementing a controller, or evaluating conformance and
feature support. Start with the upgrade hazards below, then open the topic
reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [API lifecycle and upgrades](references/api-lifecycle-and-upgrades.md) | Safe-upgrade admission, channel identities, API graduation, deprecated versions, and schema migrations |
| [Gateways, listeners, and status](references/gateways-listeners-and-status.md) | TLS coalescing, infrastructure, assigned addresses, default attachment, ListenerSet, compatibility, and status |
| [Policies, security, and capabilities](references/policies-security-and-capabilities.md) | Backend TLS, certificates, authentication, retry budgets, session persistence, and advertised features |
| [Routes, filters, and validation](references/routes-filters-and-validation.md) | HTTPRoute, GRPCRoute, TLSRoute, TCPRoute, UDPRoute, CORS, mirroring, retries, and hostname portability |

## Upgrade and migration hazards

### Keep the safe-upgrade admission policy

Gateway API installs a `ValidatingAdmissionPolicy` named
`safe-upgrades.gateway.networking.k8s.io`. It guards operations that can leave
CRDs in an unsafe or unsupported combination:

- Adding Experimental CRDs after Standard CRDs are installed is blocked.
- Downgrading to releases before the policy's supported floor is blocked.
- Monthly and older release installations are also blocked by the tightened
  policy.
- Upgrading Experimental CRDs that are already present remains permitted.

Delete the policy only for a deliberate guarded operation whose consequences
have been assessed. See
[API lifecycle and upgrades](references/api-lifecycle-and-upgrades.md).

### Recreate graduated Experimental resources

New Experimental kinds use an `X` prefix in the
`gateway.networking.x-k8s.io` API group. Experimental and Standard identities
can coexist, but graduation does not transform stored objects: recreate them
under the non-`X` kind and the Standard API group.

This matters especially for `XListenerSet`. Use the Standard `ListenerSet`
after graduation; the Experimental kind is no longer shipped.

### Migrate route and grant API versions

- Use `gateway.networking.k8s.io/v1` for `TLSRoute`, `TCPRoute`, `UDPRoute`,
  and `ReferenceGrant`.
- Treat older `TLSRoute` alpha versions and the `v1alpha2` transport-route
  versions as deprecated migration sources, not new manifest targets.
- Correct `ReferenceGrant` objects that omit `spec`; the field is mandatory.
- Kubernetes 1.31 or later is required for the stable `TLSRoute` CEL
  validation.

Read [API lifecycle and upgrades](references/api-lifecycle-and-upgrades.md)
before changing installed CRDs or stored objects.

### Update manifests for stricter schemas

Previously accepted or generated shapes can now fail validation:

- `GRPCRoute.spec` is required.
- `HTTPRoute.spec.rules` must contain at least one rule.
- `ReferenceGrant.spec` is required.
- HTTP retry codes must be unique and `attempts` must be at least `1`.
- An HTTPRoute rule may contain at most one `CORS` filter.
- Session-persistence `cookieConfig` is valid only for cookie persistence.
- Experimental session persistence no longer has `idleTimeout`.
- A Gateway infrastructure object may have at most 16 annotations.

Generated clients that modeled CORS `allowCredentials` as an enum must also be
updated to accept the Boolean value `false`.

### Recheck listener and route compatibility

- Do not attach a `TCPRoute` to a TLS listener.
- Do not assume `HTTPRoute` and `GRPCRoute` can share one hostname; an
  implementation may either allow or reject that combination.
- A healthy listener need not emit `Conflicted=False`.
- Overlapping TLS configuration can make connection coalescing unsafe and
  produce `OverlappingTLSConfig`; affected requests should receive HTTP 421.

## Gateway and listener quick reference

### Handle infrastructure failures precisely

For a missing, unsupported, or malformed Gateway infrastructure reference, set
`Accepted` with reason `InvalidParameters`. Infrastructure support is a
Standard feature.

`Gateway.spec.addresses` permits an entry without `value`. An implementation
that supports empty addresses assigns one; an implementation that does not
must report `Programmed=False` with reason `AddressNotAssigned`.

### Account for implicit and delegated attachment

Default-Gateway support allows selected Routes to attach without the usual
explicit relationship, so both controller logic and route-owner expectations
must account for the additional attachment path.

`ListenerSet` delegates listener configuration to a Gateway and can attach
across namespaces. A ListenerSet requires each listener's `port`. Gateway
status reports the number attached through `AttachedListenerSets`, while
invalid delegated listeners can use reason `ListenersNotValid`.

See
[Gateways, listeners, and status](references/gateways-listeners-and-status.md)
for attachment, compatibility, and status details.

## Policy and security quick reference

### Treat BackendTLSPolicy capabilities separately

`BackendTLSPolicy` is Standard, but not every field is Core:
`subjectAltNames` is Extended and therefore optional for implementations.
Target references receive CEL validation.

When evaluating a policy:

- Use `ResolvedRefs` for reference-resolution status.
- Apply the standardized invalid-policy and target-conflict behavior.
- Give SAN validation precedence over Hostname validation.
- Allow implementation-specific `wellKnownCACertificates` values only when
  the selected implementation documents them.
- Account for support on additional Route types.
- Permit no more than 16 certificate-authority references.

### Separate frontend and backend certificate roles

Gateway-terminated TLS client-certificate validation and selection of the
Gateway client certificate used for backend TLS are distinct Standard
features. Check both capabilities when mutual TLS spans both sides of a
Gateway.

### Validate authentication and persistence placement

External authentication began at HTTPRoute scope and also has an Experimental
Gateway-level form. Confirm the scope supported by the implementation before
placing authentication configuration.

`XBackendTrafficPolicy` combines session persistence with destination-wide
retry budgets. Use nested `budget.percent` and `budget.interval`, not the old
flat field names. Read
[Policies, security, and capabilities](references/policies-security-and-capabilities.md)
for the full policy lifecycle and feature-reporting rules.

## Route and filter quick reference

### Use percentage request mirroring deliberately

`RequestMirror` can select a percentage of requests on both `HTTPRoute` and
`GRPCRoute`. It is a Standard-channel Extended feature, so check advertised
support rather than assuming every conformant implementation provides it.

### Apply the current CORS constraints

The HTTPRoute `CORS` filter is Standard. Its relevant validation rules include:

- `allowCredentials` is Boolean and may be `false`.
- `allowMethods` cannot combine `*` with named methods.
- Origin host values must pass CEL validation.
- A rule cannot contain duplicate CORS filters.

### Name route elements and respect limits

HTTPRoute rules and matches can be named for stable identification.
`GRPCRoute` allows up to 64 matches. A `TLSRoute` can scale to 4096 hostnames
and 4096 rules, but large manifests should be tested against representative API
server, etcd, and controller capacity.

### Validate retry configuration

Within an HTTPRoute retry configuration, each status code must appear only
once and `attempts` must be at least `1`. These are schema-level constraints,
not controller-specific preferences.

See [Routes, filters, and validation](references/routes-filters-and-validation.md)
for complete route API and graduation details.

## Implementation and conformance checklist

Before accepting a Gateway API manifest or enabling a controller feature:

1. Identify whether each resource is Standard or Experimental and use its
   current API identity.
2. Check `GatewayClass.status.supportedFeatures` for optional capabilities.
3. Validate all required `spec`, rule, filter, and policy relationships.
4. Resolve listener attachment and route compatibility, including implicit
   default-Gateway attachment.
5. Emit the specified conditions and reasons for infrastructure, address, TLS,
   and ListenerSet outcomes.
6. Exercise large route objects and implementation-specific policy values in a
   representative environment.
7. Keep the safe-upgrade admission policy in place unless intentionally
   performing and reviewing a guarded operation.
