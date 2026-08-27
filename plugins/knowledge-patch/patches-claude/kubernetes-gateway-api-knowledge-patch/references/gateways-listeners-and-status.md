# Gateways, Listeners, and Status

Use this reference when reconciling Gateway infrastructure, listener
attachment, route compatibility, TLS connection reuse, or status conditions.

## TLS connection coalescing

Gateway listeners may report `OverlappingTLSConfig` when overlapping TLS
configuration makes connection coalescing unsafe (since 1.3.0).
Implementations should apply the clarified HTTPS Hostname and SNI matching
rules and return HTTP 421 for affected request cases.

Do not reduce this to ordinary hostname conflict handling: connection
coalescing can reuse an existing TLS connection, so the status and response
behavior need to reflect the unsafe reuse case.

## Gateway infrastructure

### Report invalid parameters consistently

`GatewayInfrastructure` is a Standard feature (since 1.3.0). When a Gateway
infrastructure reference is missing, unsupported, or malformed, its
`Accepted` condition should use reason `InvalidParameters`.

### Limit infrastructure annotations

Gateway infrastructure objects may contain at most 16 annotations (since
1.6.0). Validate generated annotation sets before applying them.

## Implementation-assigned addresses

`Gateway.spec.addresses` uses `[]GatewaySpecAddress`, whose `value` is optional
(since 1.3.0). `GatewayEmptyAddress` is a Standard feature.

When an address entry omits `value`:

- A supporting implementation should assign an address.
- An implementation without that support must set `Programmed=False` with
  reason `AddressNotAssigned`.

Consumers should inspect status rather than interpreting an empty value as
either success or failure on its own.

## Default Gateway attachment

The Experimental default-Gateway API lets Gateways program selected Routes by
default (since 1.4.0). This creates an attachment path beyond an explicitly
declared route-to-Gateway relationship. Controller implementations and route
owners must account for the additional attachment behavior when determining
which Gateways may claim a Route.

## ListenerSet lifecycle and behavior

### Experimental XListenerSet

`XListenerSet` can merge listeners into a single Gateway and attach across
namespaces (since 1.3.0). Each delegated listener requires `port`.

The accidentally introduced `None` option for Route namespaces was removed
before the final 1.3.0 API. Do not generate or accept manifests based on that
pre-release option.

As an Experimental `X` resource, `XListenerSet` is Extended and has no
conformance feature name. Confirm support with the selected implementation.

### Standard ListenerSet and status

`ListenerSet` graduated to the Standard channel in 1.5.0, and
`XListenerSet` stopped shipping in the Experimental channel.

Gateway status reports `AttachedListenerSets`, the number of ListenerSets that
attached successfully. ListenerSet programming can report reason
`ListenersNotValid` when delegated listeners fail validation.

## Listener and Route compatibility

### TLS listeners do not accept TCPRoute

TLS listeners no longer support `TCPRoute` (since 1.5.0). Use the Route type
supported for TLS listeners rather than relying on earlier permissive
behavior.

### HTTP and gRPC may conflict on one hostname

An implementation may either allow or reject `HTTPRoute` and `GRPCRoute`
resources on the same hostname (since 1.6.0). Portable configurations must not
assume coexistence. Separate the hostnames or verify and test the selected
implementation's behavior.

## Listener status

A listener that is not conflicted no longer needs to report an explicit
`Conflicted=False` condition (since 1.6.0). Status readers must treat absence
according to the current condition contract instead of requiring a negative
condition for every healthy listener.

## Capability status

Feature reporting through `GatewayClass.status.supportedFeatures` is Standard
since 1.4.0. Use it to discover optional controller capabilities, including
Extended features with an assigned feature name.

The Experimental `Mesh` resource introduced in 1.4.0 provides mesh-wide
configuration and reports supported features separately from Gateway
capabilities. Do not conflate its capability report with the GatewayClass
feature list.

## Reconciliation checklist

1. Validate infrastructure references and annotation count.
2. Distinguish implementation-assigned addresses from explicit addresses.
3. Include default-Gateway attachment in ownership calculations.
4. Validate delegated listeners and report attachment counts and reasons.
5. Enforce Route compatibility for each listener protocol.
6. Apply HTTPS Hostname and SNI rules before allowing coalesced connections.
7. Read optional capabilities from the appropriate Gateway or mesh status.
