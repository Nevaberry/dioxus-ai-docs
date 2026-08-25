# Networking, Security, and Observability

## Distributed message tracing

Since 2.11.0, publish with `Nats-Trace-Dest` set to an inbox to receive hop
events as a message enters or leaves servers, crosses connection types or
account boundaries, or undergoes subject mapping. `Nats-Trace-Only: true`
propagates trace events without delivering the traced message to subscribers.

```text
Nats-Trace-Dest: trace.inbox
Nats-Trace-Only: true
```

Since 2.14.0, distributed tracing preserves an existing `traceparent` header.

## JetStream replication traffic

Since 2.11.0, the per-account JetStream `cluster_traffic` setting can move an
asset's Raft replication traffic from the system account into the asset's
owning account. With multiple route connections, this can reduce cross-account
head-of-line blocking.

## Leafnode connections

### TLS-first handshake

Since 2.11.0, a leafnode TLS block may set `handshake_first` so TLS negotiation
occurs before any NATS protocol handshake.

```text
tls {
  handshake_first: true
}
```

### Isolation and remote lifecycle

Since 2.12.0, `isolate_leafnode_interest` prevents east-west interest
propagation between leafnodes that do not need direct communication. A
solicited remote may use reloadable `disabled: true` to disconnect and suppress
it, then be restored by reloading it as false.

Since 2.14.0, the entire leafnode remotes section can be added or removed by
configuration reload, extending the earlier per-remote toggle.

### Dial timeout

Since 2.14.5, `dial_timeout` is configurable globally for leafnodes or on an
individual remote. Its default is one second; increase it for high-latency
links.

```text
leafnodes {
  dial_timeout: 5s
}
```

## Route and gateway reconnection

Since 2.12.0, routes and gateways may set `connect_backoff: true` for
exponential reconnect delays from one to 30 seconds. This reduces DNS and
connection storms during restarts or outages, with slower reconnection as the
tradeoff.

## TLS cipher suites

Since 2.12.0, cipher suites newly available through Go's `crypto/tls` are
picked up automatically, while insecure suites are disabled by default. Set
`allow_insecure_cipher_suites` only when a legacy peer requires them.

## Domain-aware ACK and flow-control subjects

Since 2.14.0, servers parse both v1 and domain/account-aware v2 ACK and
flow-control subjects. They still emit v1 by default. Enable v2 emission with
this restart-only feature flag:

```text
feature_flags {
  js_ack_fc_v2: true
}
```

```text
v1: $JS.ACK.<stream>.<consumer>.<delivered>.<stream-seq>.<consumer-seq>.<timestamp>.<pending>
v2: $JS.ACK.<domain>.<account-hash>.<stream>.<consumer>.<delivered>.<stream-seq>.<consumer-seq>.<timestamp>.<pending>
```

Before enabling v2, update custom permissions or imports and exports scoped as
`$JS.ACK.<stream>.>` or `$JS.FC.<stream>.>`. Catch-all `$JS.ACK.>` and
`$JS.FC.>` rules already match both forms.

Client parsers must accept the 9-token v1 form and v2 forms with 11 or more
tokens, treating domain `_` as no domain. Always publish the supplied ACK or
flow-control reply subject unchanged.

Unknown `feature_flags` names are ignored but logged. Flags cannot be reloaded.
Remove the entire block before downgrading to a server that does not recognize
it.

## Configuration drift

Since 2.11.0, the server's `-t` flag generates a configuration-file hash and
`varz.config_digest` exposes the running configuration hash. Compare them to
detect an on-disk change that has not been loaded.

## Server and connection metadata

Since 2.12.0, `server_metadata` adds arbitrary string key/value metadata
alongside `server_tags`. Server stats report effective `GOMAXPROCS` and
`GOMEMLIMIT`. Client-related logs include account and user names, and
server-connection close logs include the remote server name.

## System events for the global account

Since 2.12.0, the global `$G` account produces system events, including client
connect and disconnect events.

## Windows TPM-backed filestore keys

Since 2.11.0 on Windows, JetStream filestore encryption keys can be protected
by the machine TPM instead of relying only on storage that may be accessible to
an attacker with physical access.

## MQTT Sparkplug B awareness

Since 2.11.0, the built-in MQTT service is Sparkplug B Aware and handles
`NBIRTH` and `NDEATH` messages.
