# Gateways, Listeners, and TLS

Use this reference when reconciling Gateways, listener sets, infrastructure
parameters, addresses, or frontend TLS behavior.

## Reconcile overlapping HTTPS listeners

Gateway API 1.3.0 clarifies HTTPS Hostname and SNI matching for connection
coalescing. When overlapping TLS configuration makes coalescing unsafe,
listeners can expose an `OverlappingTLSConfig` condition. Implementations
should return HTTP 421 for requests affected by the unsafe overlap.

Test this at the connection level: an HTTP request can reuse an existing TLS
connection, so per-request hostname routing alone is insufficient to prove
that the listener TLS configuration is safe.

## Reconcile implementation-assigned addresses

In 1.3.0, `Gateway.spec.addresses` changed to `[]GatewaySpecAddress`, and an
address entry's `value` became optional. `GatewayEmptyAddress` is a Standard
feature.

When an address value is absent:

- a supporting implementation should assign an address; or
- an implementation that cannot do so must set `Programmed=False` with
  reason `AddressNotAssigned`.

Do not reject an empty value merely because older address entries always
carried a literal address.

## Validate infrastructure parameters and annotations

When a Gateway infrastructure reference is missing, unsupported, or
malformed, its `Accepted` condition should use reason `InvalidParameters`
(1.3.0). `GatewayInfrastructure` is a Standard feature.

Gateway infrastructure objects may contain no more than 16 annotations
(1.6.0). Validate the count before producing an infrastructure object so that
controller-generated metadata does not make an otherwise valid request fail.

## Merge listeners with ListenerSet

The Experimental `XListenerSet` introduced in 1.3.0 merges listener
definitions into a Gateway and permits attachment across namespaces. Each
listener's `port` is required. The accidentally introduced `None` option for
Route namespaces was removed before the final 1.3.0 API and must not be
accepted.

`XListenerSet` was an Extended feature with no conformance feature name.
Check implementation support directly rather than inferring it from a
feature-name advertisement.

ListenerSet graduated to the Standard channel in 1.5.0, and
`XListenerSet` is no longer shipped in the Experimental channel. Recreate
objects using the Standard resource identity during migration.

## Report ListenerSet attachment and programming

Gateway status reports `AttachedListenerSets`, the number of ListenerSets
that attached successfully (1.5.0). Treat the value as successful
attachments, not as the number merely discovered or selected.

ListenerSet programming can report reason `ListenersNotValid` when invalid
listener definitions prevent programming (1.5.0). Preserve this distinction
from failures in parent selection or cross-namespace attachment.

As of 1.6.0, a listener without a conflict no longer needs an explicit
`Conflicted=False` condition. Consumers must accept absence of the condition
instead of requiring a negative condition for healthy listeners.

## Apply route compatibility at TLS listeners

TLS listeners no longer support `TCPRoute` as of 1.5.0. Use the route type
supported for TLS listeners and update any admission or attachment logic that
previously treated raw TCP routes as compatible.

## Configure Gateway-side certificates

Two Gateway certificate capabilities became Standard in 1.5.0:

- validating client certificates for TLS terminated at a Gateway; and
- selecting the Gateway client certificate used for TLS connections to
  backends.

Model the first as frontend client authentication and the second as the
Gateway's identity toward its backend. Neither replaces BackendTLSPolicy
validation of the backend server.

## Add Gateway-level authentication deliberately

Experimental authentication expanded in 1.5.0 from HTTPRoute-level external
authentication to Gateway-level configuration. Account for the wider policy
scope and interaction with route-level configuration when an implementation
enables it.
