# Migrations and deprecations

## Upgrade planning

### Upgrade paths and feature flags

For 4.1 (`4.1-guides`), direct in-place upgrades are supported from 4.0.x and
3.13.x after all stable feature flags are enabled. A 3.13 cluster that already
uses Khepri is the exception: its Khepri format is incompatible with 4.x, so
move it using a blue-green deployment. Some required feature flags are enabled
automatically at boot once every node supports them; 4.1 introduces no required
flags beyond the 4.0.x set.

For 4.2 (`4.2-guides`), direct upgrades are supported from 4.1.x, 4.0.x, and
3.13.x; an intermediate 4.1 upgrade is unnecessary. Khepri becomes the default
metadata store for new deployments, but an upgraded Mnesia deployment stays on
Mnesia until an administrator explicitly enables Khepri.

For 4.3 (`4.3-guides`), first reach 4.2.x and enable every stable feature flag.
Users starting on 3.13.x must therefore pass through 4.2.x. Khepri is the only
supported metadata store: enable `khepri_db` before the upgrade, or the first
4.3 node migrates Mnesia metadata while booting.

If AMQP 1.0 was enabled with `rabbitmq_amqp1_0` on 3.13.x and remains in use,
complete at least one rolling update after enabling `rabbitmq_4.0.0` and before
upgrading to 4.3.0 (`4.3.0`).

### Rolling-upgrade windows

- 4.1.0 nodes may temporarily coexist with 4.0.x nodes. Release-specific
  features remain unavailable until all nodes are upgraded.
- 4.2.0 nodes may temporarily coexist with 4.1.x and 4.0.x nodes (`4.2.0`).
- 4.3.0 nodes may temporarily coexist with 4.2.x nodes.
- Treat every mixed-version state as a rolling-upgrade mechanism lasting only
  a few hours, never as a steady operating mode.
- During a mixed 4.2/4.3 upgrade, local quorum-queue queries fall back to the
  older state-machine version instead of failing (`4.3.5`).

Do not use grow-then-shrink to upgrade an entire cluster. It changes replica
identities and can cause large, unnecessary data transfers. Reserve it for
replacing a single node that must be decommissioned.

### Migration tools and source artifacts

`rabbitmqadmin` v2 provides commands for automating blue-green migrations from
3.13.x to 4.2.x. For a complete 4.2.0 source distribution, use
`rabbitmq-server-4.2.0.tar.xz`; the automatically generated source archive is
not the complete distribution.

## Khepri and removed Mnesia behavior

`rabbitmqctl force_reset` is deprecated as of `4.1.0` because it is incompatible
with Khepri. In 4.3, the Mnesia-era `pause_if_all_down`, `pause_minority`, and
`autoheal` partition strategies are removed. The following settings are still
accepted but do nothing and should be deleted:

- `cluster_partition_handling`
- `cluster_partition_handling.pause_if_all_down.recover`
- `cluster_partition_handling.pause_if_all_down.nodes.$name`

Third-party plugins that need data preserved during a Mnesia-to-Khepri
migration should use the dedicated plugin data directory. Other non-whitelisted
directories beneath the node data directory can be deleted when migration
finishes.

## Queue and exchange deprecations

### Classic queue v1

Classic queue v1 storage is removed in 4.3. A declaration fails if
`x-queue-mode` is set to any value or `x-queue-version` is `1`. Convert existing
queues to CQv2 during the 4.2.x upgrade; converted queues continue to work.

### Transient non-exclusive classic queues

Non-durable, non-exclusive classic queues are rejected by default in 4.3.
Replace them with durable queues, non-durable exclusive queues, or durable
queues with a queue TTL. A temporary compatibility switch remains until final
removal:

```ini
deprecated_features.permit.transient_nonexcl_queues = true
```

STOMP subscriptions whose destinations formerly used this deprecated property
combination now use exclusive queues.

### Other deprecated features

In 4.3, `amqp_address_v1`, `amqp_filter_set_bug`, `global_qos`, and
`queue_master_locator` are denied by default and require explicit permission.
The deprecated `ram_node_type` feature is removed. The community
`rabbitmq-delayed-message-exchange` plugin is deprecated and archived; see the
extensions reference for the Tanzu delayed-queue replacement.

## Removed and ignored configuration

- The etcd peer-discovery keys
  `cluster_formation.etcd.ssl_options.fail_if_no_peer_cert`,
  `cluster_formation.etcd.ssl_options.dh`, and
  `cluster_formation.etcd.ssl_options.dhfile` are unsupported.
- Ineffective `*.cacerts` settings are removed from `rabbitmq.conf`; this does
  not remove or rename `cacertfile`.
- AMQP listener user-space buffers are auto-tuned in 4.1, so
  `tcp_listen_options.buffer` is ignored. Kernel-level `recbuf` and `sndbuf`
  settings still apply.
- `rabbitmq-streams set_stream_retention_policy` no longer changes retention
  (`4.0.6`); use a stream policy.
- The original all-in-one HTTP health check no longer performs its former
  aggregate check; use focused health endpoints.

## Tool transition

`rabbitmqadmin` 2.0 is a GA standalone binary and is preferred over v1. In
4.3, the management plugin removes the v1 download endpoint. If v1 is still
temporarily required, obtain it from the RabbitMQ `v4.2.x` source branch.
