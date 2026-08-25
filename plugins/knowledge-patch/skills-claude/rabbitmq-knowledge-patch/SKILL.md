---
name: rabbitmq-knowledge-patch
description: RabbitMQ
version: 4.3.0
license: MIT
metadata:
  author: Nevaberry
---


# RabbitMQ Compatibility Guidance

Load this skill for RabbitMQ application, plugin, operations, security,
clustering, protocol, or upgrade work. Inspect manifests, configuration,
plugins, feature flags, and installed RabbitMQ and Erlang versions first.

Treat a rolling mixed-version cluster as temporary upgrade state. Prefer the
project's actual configuration, code, tests, and observed broker behavior when
they disagree with compatibility guidance.

## Reference index

| Reference | Read for |
| --- | --- |
| [Configuration, Authentication, and Security](references/configuration-auth-and-security.md) | Authentication backends, OAuth/OIDC, TLS, authorization, credentials, and management HTTP hardening |
| [Operations, Observability, and Tooling](references/operations-observability-and-tooling.md) | Health checks, diagnostics, metrics, logs, resource controls, management API behavior, and tools |
| [Protocols, Clustering, and Federation](references/protocols-clustering-and-federation.md) | Cluster discovery, replication networking, frame limits, WebSockets, MQTT, federation, and Shovels |
| [Queues, Streams, and Messaging](references/queues-streams-and-messaging.md) | Queue and exchange declarations, quorum behavior, Streams, AMQP outcomes, filtering, and commercial features |
| [Upgrades and Deprecations](references/upgrades-and-deprecations.md) | Upgrade paths, mixed-version rules, Khepri migration, feature flags, removed settings, and runtime compatibility |

## Breaking changes and upgrade gates

### Enter 4.3 through 4.2 and Khepri

Upgrade a 4.3.x cluster only from 4.2.x after enabling all stable feature
flags. Khepri is mandatory. Enable `khepri_db` before upgrading; otherwise the
first 4.3 node migrates Mnesia metadata while booting.

For a cluster that used AMQP 1.0 on 3.13.x, complete a rolling update after
enabling `rabbitmq_4.0.0` and before moving to 4.3.0.

### Keep mixed versions short-lived

Use mixed-version clusters only for rolling upgrades, normally for no more
than a few hours. New-line features remain unavailable until all nodes finish.

Before stopping a node, protect quorum:

```shell
rabbitmq-diagnostics check_if_node_is_quorum_critical
rabbitmq-upgrade await_online_quorum_plus_one
```

Do not use grow-then-shrink for a cluster-wide upgrade; it changes replica
identities and can trigger unnecessary data transfer.

### Replace removed queue and cluster behavior

- CQv1 declarations fail when `x-queue-mode` has any value or
  `x-queue-version` is `1`. Convert queues to CQv2 on 4.2.x first.
- Non-durable, non-exclusive classic queues are rejected by default in 4.3.
  Prefer durable queues, exclusive transient queues, or durable queues with a
  queue TTL.
- Mnesia partition strategies `pause_if_all_down`, `pause_minority`, and
  `autoheal` are removed. Related accepted settings are no-ops and should be
  deleted.
- `ram_node_type` is removed. `amqp_address_v1`, `amqp_filter_set_bug`,
  `global_qos`, and `queue_master_locator` are denied by default.

Temporarily permit the deprecated queue combination only as a migration aid:

```ini
deprecated_features.permit.transient_nonexcl_queues = true
```

### Remove obsolete tools and settings

- `rabbitmqctl force_reset` is deprecated and incompatible with Khepri.
- The management plugin no longer offers the `rabbitmqadmin` v1 download;
  prefer the standalone v2 binary.
- Remove obsolete etcd TLS `fail_if_no_peer_cert`, `dh`, and `dhfile`
  settings.
- Remove ineffective `*.cacerts` settings; `cacertfile` remains supported.
- AMQP listeners auto-tune their user-space TCP buffer, so
  `tcp_listen_options.buffer` is ignored.

### Match the runtime

RabbitMQ 4.3.x requires Erlang/OTP 27.0 or later and rejects older releases.

## Queue and Stream quick reference

### Use strict quorum-queue priorities

Quorum queues have 32 strict priority levels. Higher-priority messages are
fully drained before lower-priority messages, replacing the older two-level
2:1 interleaving behavior.

### Configure native delayed retries

For quorum queues, configure `x-delayed-retry-type` as `all`, `returned`,
`failed`, or `disabled`, plus `x-delayed-retry-min` and
`x-delayed-retry-max`. Policy keys omit the `x-` prefix.

```text
delay = min(delayed-retry-min * delivery-count, delayed-retry-max)
```

AMQP 1.0 can supply per-message Unix-millisecond `x-opt-delivery-time`.

### Distinguish returns from failed deliveries

Quorum queues increment `acquired-count` for every requeue but increment
`delivery-count` only for failed attempts. Poison-message handling uses
`delivery-count`, so releases, non-failed modifications, `basic.nack`,
consumer timeouts, and suspect consumer nodes need not consume the limit.

### Apply consumer timeouts deliberately

Quorum and Tanzu JMS queues enforce consumer timeouts; classic queues and
Streams do not. Configuration precedence is:

1. Consumer `x-consumer-timeout`
2. Queue `x-consumer-timeout`
3. Policy `consumer-timeout`
4. Global `consumer_timeout`, default `1800000` ms

Use `consumer_disconnected_timeout`, policy
`consumer-disconnected-timeout`, or queue
`x-consumer-disconnected-timeout` to change the 60-second default before a
quorum queue returns messages from a disconnected consumer.

### Filter Streams on the broker

AMQP 1.0 property and application-property filters accept at most 16
properties. SQL filtering can inspect standard fields and application
properties after a Bloom-filter value skips irrelevant chunks.

## Protocol and connection quick reference

### Set current pre-authentication limits

- AMQP 0-9-1 pre-authentication frames can be up to 8192 bytes; a client
  `frame_max` override must not be lower.
- Stream Protocol pre-open frames default to 8192 bytes; adjust
  `stream.initial_frame_max` only when authentication needs more.
- A Stream connection is limited to 256 publishers and 256 subscriptions.
- `stream.max_uncompressed_sub_entry_batch_size` defaults to 64 MiB and must
  match the publisher configuration.

### Respect MQTT behavior

The default maximum MQTT packet is 16 MiB and must not exceed
`max_message_size`. MQTT 5 rejects invalid packet properties and
`Receive Maximum = 0`; it returns `Quota exceeded` in `PUBACK` when a target
queue is full.

### Harden WebSocket listeners

Web MQTT enforces `login_timeout`, bounds decompressed frames before and after
`CONNECT`, and supports origin allowlists through `web_mqtt.allow_origins`.
Web STOMP uses `web_stomp.allow_origins` and enforces accumulated frame size
against `max_frame_size`.

## Authentication and management quick reference

### Separate HTTP API authentication

Configure a distinct HTTP API backend chain when messaging protocols and the
management API use different identity systems:

```ini
auth_backends.1 = ldap
auth_backends.2 = internal
http_dispatch.auth_backends.1 = http
```

Use `rabbitmqctl clear_auth_backend_cache` for explicit invalidation. A
configured backend from a known disabled plugin prevents startup.

### Renew OAuth credentials safely

AMQP 1.0 can replace JWTs without disconnecting, but missing the expiry closes
the connection. Stream connections close immediately after failed renewal and
recheck virtual-host access after success. Refreshed credentials also replace
the connection's original user tags.

### Encrypt management UI credentials after rollout

Set the same `management.credential_encryption_secret` on every node. Enable
it only after the rolling upgrade, because older nodes reject the resulting
AES-256-GCM `rmqe.` bearer tokens.

### Protect management actions

- Tag users `protected` to prevent HTTP API modification or deletion.
- Require `policymaker` for federation link restarts and Shovel deletion.
- Set `management.require_auth_for_api_reference = true` to protect `/api`.
- Enable `auth_http.authorization_failure_disclosure` only when custom denial
  reasons should be disclosed to AMQP clients.

## Operations quick reference

### Replace broad health checks

The old all-in-one HTTP health check is a no-op. Use focused metadata-store,
connection-limit, listener, boot-state, and maintenance-state checks.

### Update Ra dashboards for 4.2 metrics

The `rabbitmq_raft*` and `rabbitmq_detailed_raft*` families changed. Update the
quorum-queue Raft Grafana dashboard and dependent alerts together.

### Limit diagnostic overhead

Use `log.summarize_process_state` and `log.error_logger_format_depth` to avoid
large queue-member crash reports causing allocation spikes. On supported Unix
systems, `RABBITMQ_MAX_OPEN_FILES` can raise a soft limit when the hard limit
is already sufficient.

### Keep resource alarms authoritative

MQTT, STOMP, and Web MQTT stay blocked until every active memory and disk
alarm clears. Direct AMQP 0-9-1 Shovel connections are also blocked by
resource alarms.

## Cluster and federation quick reference

### Configure discovery intentionally

Set `cluster_formation.registration.enabled = false` when Consul should
discover peers but another system owns service registration. Use
`cluster_formation.discovery_retry_limit = infinity` for unbounded discovery
retries.

Kubernetes discovery uses node index `0` as the initial seed without calling
the Kubernetes API. AWS discovery can use IPv6 endpoints in IPv6-only
environments.

### Choose the Stream replication address family

Select IPv4 or IPv6 for Stream replication in `rabbitmq.conf`; older
deployments can use the Osiris `replica_ip_address_family` setting in
`advanced.config`.

### Choose the correct Shovel mode

Use `local` only for consuming and publishing inside one cluster. It reuses
internal AMQP 1.0 paths and cannot connect separate clusters. Use
`src-consumer-name` for a stable source consumer identity and
`src-delete-after-duration` for self-deleting dynamic Shovels.
