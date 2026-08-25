# Upgrades and Deprecations

Use this reference before changing RabbitMQ or Erlang versions, metadata
stores, feature flags, deprecated features, or cluster membership during an
upgrade.

## Choose a supported path (4.1-guides, 4.2-guides, 4.3-guides)

### Direct upgrade paths and the Khepri exception

RabbitMQ 4.1 accepts direct upgrades from 4.0.x and 3.13.x after every stable
feature flag is enabled. A 3.13 cluster already using Khepri cannot upgrade in
place because its Khepri format is incompatible; use blue-green migration.

### Direct upgrade paths to 4.2

RabbitMQ 4.2 accepts direct upgrades from 4.1.x, 4.0.x, or 3.13.x. The older
lines do not need an intermediate 4.1 upgrade.

### 4.3 upgrade path and mandatory Khepri

Upgrade to 4.3.x only from 4.2.x and first enable every stable feature flag.
Users on 3.13.x must pass through 4.2.x. Khepri is the only supported metadata
store: enable `khepri_db` before upgrading or the first 4.3 node migrates
Mnesia metadata during boot.

## Keep rolling upgrades temporary (4.1-guides, 4.2.0, 4.3.0, 4.3.5)

### Mixed-version rolling upgrades

4.1.0 nodes can temporarily coexist with 4.0.x nodes, but 4.1-only features
remain unavailable until all nodes are upgraded. Use mixed versions only as an
upgrade mechanism, for no more than a few hours.

### 4.2 rolling-upgrade compatibility

4.2.0 nodes can temporarily coexist with 4.1.x and 4.0.x nodes. Do not use
4.2-only features until every node is on 4.2.0 or later in the series, and do
not keep the cluster mixed for more than a few hours.

### 4.3 rolling-upgrade compatibility

4.3.0 and 4.2.x nodes can temporarily coexist during a rolling upgrade. Keep
the mixed state to no more than a few hours.

### Mixed-version quorum-queue queries

During a mixed 4.2.x/4.3.x rolling upgrade, local quorum-queue queries fall
back to the earlier state-machine version instead of failing.

### Grow-then-shrink is not a cluster-wide upgrade strategy

Do not use grow-then-shrink for an entire cluster: changing replica identities
can cause large unnecessary transfers. It remains suitable for replacing one
node that must be decommissioned.

## Protect quorum and client readiness (4.1-guides)

### Quorum-safe node shutdown

Before stopping a node, verify that no quorum queue, Stream, or internal
component would lose online quorum. Automation can wait for quorum-plus-one:

```shell
rabbitmq-diagnostics check_if_node_is_quorum_critical
rabbitmq-upgrade await_online_quorum_plus_one
```

### Management UI state after an upgrade

After the cluster upgrade, clear browser cache, local storage, session storage,
and cookies for management UI domains to prevent stale-client JavaScript
errors.

## Sequence feature flags and metadata migration (4.1-guides, 4.2-guides, 4.2.0, 4.3.0)

### Required feature flags at boot

Some required flags enable automatically at boot once every cluster node
supports them. RabbitMQ 4.1 adds no required flags beyond the 4.0.x set.

### Khepri is the default metadata store

Khepri is the default for new 4.2 deployments. An upgraded deployment already
using Mnesia remains on Mnesia until an administrator explicitly enables
Khepri; the default does not silently migrate it.

### Third-party plugin data during Khepri migration

Plugins can use the dedicated directory preserved during Mnesia-to-Khepri
migration. Other non-whitelisted directories in the node data directory can
be deleted when migration finishes.

### AMQP 1.0 feature-flag upgrade ordering

If `rabbitmq_amqp1_0` was enabled on 3.13.x and AMQP 1.0 remains in use on
4.x, complete at least one rolling update after enabling `rabbitmq_4.0.0` and
before upgrading to 4.3.0.

## Automate major-version migration (4.2.0)

### Automated 3.13-to-4.2 blue-green migrations

`rabbitmqadmin` v2 includes commands intended to automate blue-green migration
from 3.13.x clusters to 4.2.x.

## Remove obsolete settings and commands (4.1-guides, 4.1.0, 4.3-guides, 4.3.0)

### Removed etcd TLS settings

Remove unsupported `cluster_formation.etcd.ssl_options.fail_if_no_peer_cert`,
`cluster_formation.etcd.ssl_options.dh`, and
`cluster_formation.etcd.ssl_options.dhfile` settings.

### `force_reset` deprecation

`rabbitmqctl force_reset` is deprecated because it is incompatible with
Khepri.

### Removed partition-handling configuration

The Mnesia-era `pause_if_all_down`, `pause_minority`, and `autoheal` strategies
are removed. `cluster_partition_handling`,
`cluster_partition_handling.pause_if_all_down.recover`, and
`cluster_partition_handling.pause_if_all_down.nodes.$name` are accepted but
have no effect; remove them.

### Classic queue v1 storage removed

CQv1 declarations fail if `x-queue-mode` has any value or `x-queue-version`
is `1`. Queues converted to CQv2 during a 4.2.x upgrade continue to work.

### Additional deprecated features denied or removed

`amqp_address_v1`, `amqp_filter_set_bug`, `global_qos`, and
`queue_master_locator` are denied by default and require explicit opt-in.
`ram_node_type` has been removed.

### `rabbitmqadmin` v1 download endpoint removed

The management plugin no longer serves the v1 download. Use
`rabbitmqadmin` v2 or obtain v1 from the RabbitMQ `v4.2.x` source branch.

## Replace transient non-exclusive queues (4.3-guides)

### Transient non-exclusive queues disabled by default

Declarations of non-durable, non-exclusive classic queues are rejected by
default. Use durable queues, non-durable exclusive queues, or durable queues
with queue TTL. The deprecated combination can be re-enabled temporarily:

```ini
deprecated_features.permit.transient_nonexcl_queues = true
```

## Match the Erlang runtime (4.1-guides, 4.3.5)

### Erlang compatibility

RabbitMQ 4.1 requires Erlang/OTP 26.2 or later and supports the Erlang/OTP 27.x
series.

### Erlang/OTP 27 minimum

RabbitMQ 4.3.x requires Erlang/OTP 27.0 or later and refuses to start on older
runtimes.
