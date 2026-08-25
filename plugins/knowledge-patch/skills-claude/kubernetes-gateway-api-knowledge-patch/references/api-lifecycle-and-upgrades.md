# API Lifecycle and Upgrades

Use this reference when installing CRDs, changing release channels, migrating
stored objects, or updating manifests to graduated APIs.

## Safe-upgrade admission

### The admission policy guards CRD transitions

Gateway API installs the `safe-upgrades.gateway.networking.k8s.io`
`ValidatingAdmissionPolicy` (since 1.5.0). It blocks:

- Adding Experimental CRDs after Standard CRDs have already been installed.
- Downgrading to a release before 1.5.

It does not block upgrades of Experimental CRDs that are already present.
Delete the policy first only when deliberately performing one of the guarded
operations after assessing its safety.

The policy gained more restrictions in 1.6.0: it also prevents installation of
monthly Gateway API releases and older releases.

## Experimental and Standard identities

### Experimental kinds use a separate identity

New Experimental kinds use an `X` prefix and the
`gateway.networking.x-k8s.io` API group (since 1.3.0). They can coexist with
Standard resources. Graduation requires object recreation under the non-`X`
kind and non-`x-k8s` API group; changing installed CRDs alone does not migrate
objects.

`XListenerSet` and `XBackendTrafficPolicy` were introduced under this rule.
Both are Extended features and have no conformance feature name, so check
support directly with the implementation.

### ListenerSet graduated

`ListenerSet` moved to the Standard channel in 1.5.0. `XListenerSet` is no
longer shipped in the Experimental channel, so recreate delegated-listener
objects with the Standard identity during migration.

The HTTPRoute CORS filter graduated to Standard in the same release. Its
resource lifecycle and validation are detailed in
[Routes, filters, and validation](routes-filters-and-validation.md).

## TLSRoute migration

### The last Experimental shape tightened validation

Experimental `TLSRoute` moved to `v1alpha3` in 1.4.0. In that version:

- `hostnames` is required.
- `rules` is limited to one item.

Migrate older manifests before adopting this schema.

### TLSRoute is stable

`TLSRoute` graduated to `gateway.networking.k8s.io/v1` in 1.5.0.
`v1alpha2` and `v1alpha3` are deprecated, and `v1alpha2` is no longer shipped
in the Experimental channel. The CEL validation used by the stable API
requires Kubernetes 1.31 or later.

In 1.6.0, the stable resource permits up to 4096 hostnames and 4096 rules.
Before relying on those limits in production, validate API server, etcd, and
controller behavior with representative large manifests.

## ReferenceGrant migration

`ReferenceGrant` graduated to `gateway.networking.k8s.io/v1` in 1.5.0.
Starting in 1.6.0, `ReferenceGrant.spec` is mandatory; manifests that omit it
are rejected by schema validation.

## TCPRoute and UDPRoute migration

`TCPRoute` and `UDPRoute` graduated to `gateway.networking.k8s.io/v1` in
1.6.0. Their `v1alpha2` versions are deprecated and will be removed.

Conformance now includes:

- A `GATEWAY-UDP` profile.
- A `SupportTCPRoute` feature.

Use these signals when testing a controller, but still check listener
compatibility: a TLS listener does not support `TCPRoute`.

## Migration checklist

1. Leave the safe-upgrade admission policy installed during normal upgrades.
2. Inventory Experimental objects whose identities change on graduation.
3. Recreate graduated objects under their Standard kind and API group.
4. Move TLS, TCP, UDP, and grant manifests to their stable `v1` APIs.
5. Correct newly required fields before applying upgraded CRD schemas.
6. Check the cluster version before relying on stable `TLSRoute` CEL
   validation.
7. Run implementation conformance tests for the Route types actually used.
