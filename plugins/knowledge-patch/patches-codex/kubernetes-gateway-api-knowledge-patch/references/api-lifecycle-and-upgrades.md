# API Lifecycle and Upgrades

Use this reference when installing CRDs, changing release families or
channels, or migrating manifests to graduated resource versions. Entries are
grouped by upgrade task rather than release chronology.

## Guard CRD installation and downgrade operations

Gateway API 1.5.0 installs
`safe-upgrades.gateway.networking.k8s.io`, a
`ValidatingAdmissionPolicy` that prevents two hazardous operations:

- adding Experimental CRDs after Standard CRDs have been installed; and
- downgrading to a release before 1.5.

The policy still permits upgrades of Experimental CRDs already installed.
Delete it only when deliberately performing a guarded operation after
assessing the compatibility and data-safety consequences.

In 1.6.0, the policy also prevents installation of monthly Gateway API
releases and older releases. A blocked installation is therefore expected
policy behavior, not evidence that the CRD bundle itself is malformed.

## Keep Experimental and Standard identities distinct

Starting in 1.3.0, new experimental kinds use an `X` prefix and the
`gateway.networking.x-k8s.io` API group. Experimental and Standard kinds can
coexist. If an experimental kind graduates, recreate the object under the
non-X kind and non-X API group; identity does not migrate in place.

The first resources following this convention were `XListenerSet` and
`XBackendTrafficPolicy`. Both were Extended features without conformance
feature names, so support had to be checked with each implementation.

In 1.5.0, ListenerSet and the HTTPRoute CORS filter graduated to the Standard
channel. `XListenerSet` stopped shipping in the Experimental channel. Migrate
ListenerSet objects to their Standard identity instead of expecting the old
CRD to remain available.

## Migrate TLSRoute schemas and versions

The Experimental TLSRoute schema changed in 1.4.0:

- the API version moved to `v1alpha3`;
- `hostnames` became required; and
- `rules` was limited to one item.

Migrate older manifests before submitting them to that schema.

TLSRoute became GA at `gateway.networking.k8s.io/v1` in 1.5.0.
`v1alpha2` and `v1alpha3` are deprecated, and `v1alpha2` is no longer shipped
in the Experimental channel. The stable TLSRoute CEL validation requires
Kubernetes 1.31 or later, so verify the cluster version before installing
those CRDs.

## Migrate TCPRoute and UDPRoute

TCPRoute and UDPRoute graduated to `gateway.networking.k8s.io/v1` in 1.6.0.
Their `v1alpha2` forms are deprecated and will be removed. Update manifests,
generated clients, and controller watches to the stable group/version.

Conformance now includes a `GATEWAY-UDP` profile and a `SupportTCPRoute`
feature. Use those surfaces when verifying that an implementation supports
the graduated route types.

## Migrate ReferenceGrant

ReferenceGrant moved to `gateway.networking.k8s.io/v1` in 1.5.0. Update
manifests and clients to the stable version.

Beginning with 1.6.0, `ReferenceGrant.spec` is mandatory. Objects that omit
the field are rejected by schema validation, so generators must emit `spec`
even when constructing the object incrementally.

## Prepare generated clients for schema corrections

In 1.4.0, GRPCRoute's top-level `spec` became required after having been
accidentally optional through `omitempty`. Previously stored objects without
`spec` were unusable; correct them before installing or enforcing the newer
schema.

Also in 1.4.0, the Experimental CORS filter began accepting
`allowCredentials: false`. Generated API libraries must represent the field
as a Boolean rather than relying on the earlier enum representation.

In 1.5.0, `HTTPRoute.spec.rules` gained a minimum size of one. Admission now
rejects an absent or empty rule list.

## Remove retired fields

The Experimental SessionPersistence API removed `idleTimeout` in 1.6.0.
Remove that field from manifests, custom types, serialization tests, and
generated configuration before upgrading the CRDs.
