# Networking and Accounts

## Distributed message tracing

Since 2.11.0, publish with `Nats-Trace-Dest` set to an inbox to receive hop
events when the message enters or leaves servers, crosses connection types or
account boundaries, or undergoes subject mapping. `Nats-Trace-Only: true`
propagates events without delivering the traced message.

```text
Nats-Trace-Dest: trace.inbox
Nats-Trace-Only: true
```

Since 2.14.0, tracing preserves an existing `traceparent` header rather than
modifying it.

## Per-account JetStream replication traffic

The per-account `cluster_traffic` setting (since 2.11.0) moves an asset's Raft
replication traffic from the system account to the account that owns the asset.
With multiple route connections, this can reduce cross-account head-of-line
blocking.

## Domain-aware ACK and flow-control subjects

Servers since 2.14.0 parse legacy v1 and domain/account-aware v2 ACK and
flow-control subjects. They still emit v1 by default. Opt into v2 emission with
the restart-only flag:

```text
feature_flags {
  js_ack_fc_v2: true
}
```

```text
v1: $JS.ACK.<stream>.<consumer>.<delivered>.<stream-seq>.<consumer-seq>.<timestamp>.<pending>
v2: $JS.ACK.<domain>.<account-hash>.<stream>.<consumer>.<delivered>.<stream-seq>.<consumer-seq>.<timestamp>.<pending>
```

Update custom permissions or imports/exports scoped as `$JS.ACK.<stream>.>` or
`$JS.FC.<stream>.>` before enabling v2. Catch-all `$JS.ACK.>` and `$JS.FC.>`
rules match both layouts. Client parsers must accept the nine-token v1 form and
v2 forms of eleven or more tokens, interpret domain `_` as no domain, and
publish the supplied ACK or flow-control reply subject unchanged.

Unknown names inside `feature_flags` are ignored but logged. Flags cannot be
reloaded. Remove the entire block before downgrading to a server that does not
recognize it.

## Leafnode TLS-first handshakes

Since 2.11.0, a leafnode TLS block can set `handshake_first: true` so TLS
negotiation completes before the NATS protocol handshake.

```text
tls {
  handshake_first: true
}
```

## Leafnode isolation and reloadable remotes

`isolate_leafnode_interest` (since 2.12.0) stops east-west interest propagation
between leafnodes that do not need direct communication. A solicited remote can
also be disconnected and suppressed on reload with `disabled: true`, then
re-enabled by reloading it as false.

Since 2.14.0, the entire leafnode remotes section can be added or removed on
configuration reload without a server restart.

## Leafnode dial timeout

Since 2.14.5, `dial_timeout` is configurable for all leafnodes or one individual
remote. The default is one second; raise it for high-latency links.

```text
leafnodes {
  dial_timeout: 5s
}
```

## Route and gateway reconnection backoff

Routes and gateways since 2.12.0 can set `connect_backoff: true` for exponential
reconnect delays from one to 30 seconds. This reduces DNS and connection storms
during restarts or outages, with slower reconnection as the tradeoff.

## TLS cipher-suite defaults

Since 2.12.0, cipher suites newly provided through Go `crypto/tls` are selected
automatically, while insecure suites are disabled by default. Set
`allow_insecure_cipher_suites` only when a legacy peer still requires them.

## MQTT Sparkplug B awareness

The built-in MQTT service is Sparkplug B Aware since 2.11.0 and handles `NBIRTH`
and `NDEATH` messages.

## Server and connection metadata

`server_metadata` (since 2.12.0) adds arbitrary string key/value metadata
alongside `server_tags`. Server stats report effective `GOMAXPROCS` and
`GOMEMLIMIT`. Client-related logs include account and user names, while
server-connection close logs include the remote server name.

## Global-account system events

Since 2.12.0, the global `$G` account produces system events, including client
connect and disconnect events.
