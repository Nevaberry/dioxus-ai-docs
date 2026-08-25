---
name: rabbitmq-knowledge-patch
description: RabbitMQ
version: 4.3.0
license: MIT
metadata:
  author: Nevaberry
---


# RabbitMQ Knowledge Patch

Use this skill when upgrading or operating RabbitMQ, changing broker or plugin
configuration, integrating a protocol client, or updating monitoring and
automation. Determine the deployed RabbitMQ and Erlang/OTP versions first, then
open the reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations-and-deprecations.md](references/migrations-and-deprecations.md) | Upgrade paths, rolling upgrades, Khepri migration, removed settings and deprecated features |
| [clustering-configuration-and-operations.md](references/clustering-configuration-and-operations.md) | Cluster formation, feature flags, resource alarms, health checks, limits, diagnostics, Erlang compatibility |
| [queues-streams-and-exchanges.md](references/queues-streams-and-exchanges.md) | Queue semantics, quorum queues, streams, exchange limits and routing behavior |
| [protocols-and-clients.md](references/protocols-and-clients.md) | AMQP 1.0, AMQP 0-9-1, MQTT, STOMP, WebSocket, Direct Reply-To, client behavior |
| [security-and-authentication.md](references/security-and-authentication.md) | OAuth/OIDC, LDAP, TLS, authentication backends, authorization, credential refresh |
| [management-api-and-observability.md](references/management-api-and-observability.md) | HTTP API, management UI, Prometheus metrics, logging, definition import/export |
| [federation-shovels-and-extensions.md](references/federation-shovels-and-extensions.md) | Federation, Shovels, plugin APIs, peer discovery, Tanzu features |

## Upgrade decision points

### Moving to 4.3

- Upgrade through 4.2.x; 4.3.x accepts upgrades only from 4.2.x.
- Enable all stable feature flags before the upgrade.
- Khepri is mandatory. Enable `khepri_db` before the first 4.3 node starts, or
  that node migrates Mnesia metadata during boot.
- If the cluster used AMQP 1.0 on 3.13 with `rabbitmq_amqp1_0` enabled, complete
  a rolling update after enabling `rabbitmq_4.0.0` and before entering 4.3.
- Keep a 4.3/4.2 mixed cluster only for the few hours required by a rolling
  upgrade.
- Run 4.3.x on Erlang/OTP 27.0 or later; older runtimes do not start.

### Moving to 4.2 or 4.1

- 4.2 accepts direct upgrades from 4.1.x, 4.0.x, or 3.13.x. Existing Mnesia
  deployments remain on Mnesia until Khepri is explicitly enabled.
- 4.1 accepts 4.0.x or 3.13.x after all stable feature flags are enabled.
- A 3.13 cluster already using Khepri cannot upgrade in place to 4.x because
  the metadata format is incompatible; use a blue-green migration.
- Mixed-version clusters exist only for rolling upgrades. Do not enable
  release-specific features until every node has reached the new series.
- Do not use grow-then-shrink as a whole-cluster upgrade strategy; it changes
  replica identities and can cause large data transfers.

## Breaking removals and defaults

### Metadata and partition handling

- 4.3 supports Khepri only. Remove Mnesia-era partition settings:
  `pause_if_all_down`, `pause_minority`, and `autoheal`.
- The accepted keys `cluster_partition_handling`,
  `cluster_partition_handling.pause_if_all_down.recover`, and
  `cluster_partition_handling.pause_if_all_down.nodes.$name` are inert.
- `rabbitmqctl force_reset` is deprecated because it is incompatible with
  Khepri.

### Queues and deprecated features

- Classic queue v1 storage is gone. Declarations fail if `x-queue-mode` has
  any value or `x-queue-version` is `1`; convert queues to CQv2 on 4.2 first.
- Non-durable, non-exclusive classic queues are rejected by default. Prefer a
  durable queue, an exclusive transient queue, or a durable queue with TTL.
  Temporary compatibility requires
  `deprecated_features.permit.transient_nonexcl_queues = true`.
- `amqp_address_v1`, `amqp_filter_set_bug`, `global_qos`, and
  `queue_master_locator` are denied unless explicitly permitted.
  `ram_node_type` has been removed.
- Administrators can disable individual queue types; clients then cannot
  declare new queues or streams of those types.

### Removed or ignored settings and tools

- The management plugin no longer serves the `rabbitmqadmin` v1 download.
  Prefer the standalone `rabbitmqadmin` v2.
- `rabbitmq-streams set_stream_retention_policy` is a no-op; set retention by
  policy.
- The legacy all-in-one HTTP health check is a no-op; use focused checks.
- `tcp_listen_options.buffer` is ignored because AMQP user-space TCP buffers
  are auto-tuned. Kernel `recbuf` and `sndbuf` still apply.
- Remove ineffective `*.cacerts` settings, but retain `cacertfile` where used.
- Remove the obsolete etcd TLS keys `fail_if_no_peer_cert`, `dh`, and `dhfile`.

## Queue and stream behavior to re-test

### Quorum queues

- Quorum queues use 32 strict priority levels: every higher priority is
  delivered before a lower one. This replaces the former two-level 2:1
  interleaving behavior.
- Native delayed retries use `x-delayed-retry-type`,
  `x-delayed-retry-min`, and `x-delayed-retry-max`, or their policy forms.
- Requeue attempts increment `acquired-count`, but only failures increment
  `delivery-count`; poison-message limits therefore do not necessarily count
  ordinary returns.
- Consumer timeout precedence is consumer argument, queue argument, policy,
  then global `consumer_timeout`. Timeouts affect quorum and Tanzu JMS queues,
  not classic queues or streams.
- `consumer_disconnected_timeout` defaults to 60 seconds before a partitioned
  consumer's messages are returned. Policy and per-queue overrides exist.
- Delivery limits are policy-mutable. Purging also removes pending
  at-least-once dead-lettered messages.

### Streams

- AMQP 1.0 consumers can combine chunk-level filter values with broker-side
  SQL expressions over message fields and application properties.
- Stream connections allow at most 256 publishers and 256 subscriptions.
- Before a successful `open`, Stream frames default to an 8192-byte ceiling,
  configurable with `stream.initial_frame_max`.
- `stream.max_uncompressed_sub_entry_batch_size` defaults to 64 MiB; configure
  publishers to the same decompression ceiling.
- A failed Stream OAuth renewal closes the connection, and the renewed token
  is reauthorized for the active virtual host.

### Exchanges and routing

- A topic binding key may contain at most two `#` wildcards; prefer one final
  `#` segment.
- `x-modulus-hash` is now a core exchange and has restart-stable distribution
  while bindings remain stable.
- `cluster_exchange_limit` caps application declarations cluster-wide and
  must have the same value on every node.
- The local-random exchange type can be disabled with
  `exchange_types.local_random.enabled = false`.

## Protocol compatibility checks

### AMQP

- An AMQP 1.0 message without a header now uses the specification default
  `durable = false`; send an explicit durable header when required.
- AMQP 1.0 supports dynamic nodes, Direct Reply-To, OAuth token renewal,
  multiple routing keys through string-list annotation `x-cc`, and stream
  filters. Property filters are limited to 16 properties.
- AMQP 0-9-1 clients must offer a pre-authentication `frame_max` of at least
  8192. Node.js `amqplib` should be 0.10.7 or newer.
- Credential refresh clears AMQP 0-9-1 permission caches, revalidates
  consumers, and refreshes user tags. Passive declarations require
  `configure` permission.

### MQTT, STOMP, and WebSocket

- MQTT's default maximum packet size is 16 MiB and must not exceed the broker
  `max_message_size`.
- MQTT 5 rejects packet-invalid properties and `Receive Maximum = 0`, and
  reports `Quota exceeded` when a queue length limit rejects a publish.
- Web MQTT enforces pre/post-authentication decompressed-frame ceilings,
  `login_timeout`, and optional origin allowlists. Web STOMP enforces its frame
  limit during accumulation.
- MQTT, STOMP, and Web MQTT stay blocked until all active resource alarms have
  cleared.
- STOMP destinations affected by the transient non-exclusive queue removal use
  exclusive queues.

## Security and management checks

- Configure OAuth providers explicitly; do not rely on former Azure Entra or
  Auth0 defaults. Discovery endpoints, scope aliases, selected variables, and
  forwarded proxy headers are supported.
- Plain secrets containing a colon are not encrypted. Prefix supported
  encrypted values with `encrypted:`.
- A configured backend from a known but disabled authentication plugin causes
  startup to fail.
- HTTP API authentication can use a backend chain separate from messaging
  protocols. Protect the API reference and sensitive users where appropriate.
- Management actions that restart federation links or delete Shovels require
  the `policymaker` tag.
- When enabling encrypted management UI credentials, use the same
  `management.credential_encryption_secret` on every node and wait until the
  rolling upgrade is complete.

## Operational validation

Before stopping a node, run:

```shell
rabbitmq-diagnostics check_if_node_is_quorum_critical
rabbitmq-upgrade await_online_quorum_plus_one
```

For metadata readiness and quorum leadership, use the focused diagnostics:

```shell
rabbitmq-diagnostics check_if_metadata_store_is_initialized
rabbitmq-diagnostics check_if_metadata_store_is_initialized_with_data
rabbitmq-diagnostics check_for_quorum_queues_without_an_elected_leader \
  --vhost "vh-1" "^naming-pattern"
```

Also update 4.2-era Raft metric names and Grafana dashboards, clear stale
management UI browser state after an upgrade, and validate the exact deployed
configuration against the matching topic reference.
