# Upgrades and Lifecycle

## Enterprise license transition

For the `1.21-upgrade` procedure to Consul 1.21.7+ent or later with the updated
license, upgrade server agents before client agents. Apply `enterprise-standard`
to both groups, but restart only the servers first, one at a time. Clients can
continue using the existing license until the servers are ready; then restart
clients with the new license.

## Maintained-version cadence

Routine upgrades should span at most two major Consul version jumps. For
example, when `1.21.x` is current, begin from no earlier than `1.19.x`.

- Community operators generally move to the latest major release about every
  four months.
- Standard Enterprise majors are maintained for about one year.
- Enterprise LTS releases are maintained for about two years; operators can
  upgrade about annually and jump at most three major versions.

Treat these as planning bounds and confirm direct upgrade support before any
rollout.

## Server, client, and Envoy rollout order

Restart server agents one at a time. Wait for each to become healthy and rejoin
before continuing, then roll client agents.

On a service-mesh client:

1. Stop the old Consul agent.
2. Stop its associated Envoy proxies.
3. Start the new Consul agent.
4. Start Envoy versions compatible with the new agent.
5. Run `consul members` to confirm every agent's build and protocol.

## Federated service-mesh preparation

WAN-federated mesh clients should use centralized sidecar and mesh-gateway
configuration:

```hcl
enable_central_service_config = true
```

Consul 1.8.4 or later reports compatible Envoy versions through
`/v1/agent/self`. If old and new Consul versions both support the installed
Envoy version, the proxies may not require an immediate upgrade.

## Two-phase protocol transitions

When release notes require an incompatible protocol transition, first run the
new binary while speaking the previous protocol:

```shell
consul -v
consul agent -protocol=PREVIOUS
```

Keep server restarts one at a time and wait for each server to rejoin. After
every node runs the new binary, restart all agents without the override. The
`-protocol` flag changes only the protocol spoken, not the complete understood
range; an older spoken protocol can disable newer features.

## WAN-federated rollout order

Upgrade the primary datacenter's servers, then its clients. Repeat servers then
clients for each secondary datacenter.

Within a server set:

1. Identify the leader with `consul operator raft list-peers`.
2. Upgrade followers before the leader.
3. Run `consul leave` on one server and wait for `left`.
4. Start its new binary and wait for `alive`.
5. Continue one server at a time to preserve quorum.

## Client availability and ACL token restoration

From `consul leave` until a client agent restarts, its services are unhealthy
and undiscoverable. Zero-downtime upgrades therefore require redundant service
instances on other clients.

If `enable_token_persistence` was not enabled and a server's tokens are absent
from its configuration files, reapply the `agent` and `default` tokens after
restart before the server can rejoin.

## Federated ACL verification

After all datacenters are upgraded, check WAN membership:

```shell
consul members -wan
```

Then query ACL replication from a secondary datacenter agent:

```shell
curl -s -H "X-Consul-Token: $CONSUL_HTTP_TOKEN" \
  "https://consul-server-0.secondary/v1/acl/replication?pretty"
```

The primary datacenter always reports ACL replication as disabled, including
when replication is working.

## Autopilot server-set replacement

Consul Enterprise automated upgrades are enabled by default when
`DisableUpgradeMigration` is `false`. New-version servers initially join as
non-voters. After enough replacements form a quorum, Autopilot promotes them,
transfers leadership to the new server set, and demotes the old servers. Remove
the old servers with `consul leave`. The versions must still support a direct
upgrade.

```shell
consul operator autopilot get-config
consul operator autopilot set-config -disable-upgrade-migration=false
```

## Version-tagged node migrations

For an image, operating-system, or configuration replacement that does not
change the Consul binary, set `UpgradeVersionTag` to a `node_meta` key.
Autopilot compares that key as a semantic version in `X`, `X.Y`, or `X.Y.Z`
form instead of comparing Consul versions.

Tag existing servers with the old value and reload them before joining
replacements with a newer value:

```hcl
node_meta {
  build = "0.0.2"
}
autopilot {
  upgrade_version_tag = "build"
}
```
