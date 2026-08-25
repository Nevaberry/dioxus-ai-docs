# Upgrades and Rollouts

## Update Enterprise licenses in the required order

For the 1.21-upgrade path to Consul 1.21.7+ent or later with the updated license:

1. Configure the updated `enterprise-standard` license for both servers and clients.
2. Restart only server agents first, one at a time.
3. Wait until the upgraded servers are ready.
4. Restart client agents with the new license.

Clients continue using the existing license until the server rollout is complete. Do not restart clients ahead of the servers.

## Stay within a maintained upgrade path

Routine upgrades should span at most two major Consul version jumps. For example, when `1.21.x` is current, begin from no earlier than `1.19.x`.

Operational cadence differs by edition:

- Community operators generally move to the latest major release about every four months.
- Enterprise LTS operators can upgrade about annually and jump at most three major versions.
- Standard Enterprise major releases are maintained for about one year.
- Enterprise LTS releases are maintained for about two years.

These limits still require the selected old and new versions to support a direct upgrade.

## Roll agents and Envoy in order

Restart server agents on the new Consul version one at a time. Wait for each server to become healthy and rejoin before proceeding, then roll client agents.

On a service-mesh client:

1. Stop the old Consul agent.
2. Stop its associated Envoy proxies.
3. Start the new Consul agent.
4. Start Envoy proxies that are compatible with the new agent.

Use `consul members` to confirm every agent's build and protocol.

## Prepare a WAN-federated service mesh

Before a federated rollout, enable centralized sidecar and mesh-gateway configuration:

```hcl
enable_central_service_config = true
```

Consul 1.8.4 and later reports compatible Envoy versions through `/v1/agent/self`. If the old and new Consul versions both support the installed Envoy version, the Envoy upgrade need not occur immediately.

## Perform a two-phase protocol transition

When release notes require an incompatible protocol change, first run the new Consul binary while it speaks the previous protocol:

```shell
consul -v
consul agent -protocol=PREVIOUS
```

Keep server restarts one at a time and wait for each to rejoin. After every node runs the new binary, restart every agent again without the override.

`-protocol` changes only the version the agent speaks, not the complete protocol range it understands. Holding an older protocol can disable newer features, so remove the override after the binary rollout.

## Preserve quorum across federated datacenters

Upgrade the primary datacenter's servers and then its clients. Repeat servers then clients for each secondary datacenter.

For each server set:

1. Identify the Raft leader with `consul operator raft list-peers`.
2. Upgrade followers first and the leader last.
3. On each server, run `consul leave` and wait for state `left`.
4. Start the new binary and wait for state `alive` before continuing.

This sequence preserves quorum.

## Protect client availability and restore tokens

From `consul leave` until a client agent restarts, that client's services are unhealthy and undiscoverable. Zero downtime requires redundant service instances on other clients.

If `enable_token_persistence` was not enabled and a server's tokens are absent from configuration files, reapply its `agent` and `default` tokens after restart. The agent cannot rejoin until the required tokens are restored.

## Verify federated ACL replication

After all datacenters are upgraded, verify WAN membership:

```shell
consul members -wan
```

Then query `/v1/acl/replication` on a secondary-datacenter agent:

```shell
curl -s -H "X-Consul-Token: $CONSUL_HTTP_TOKEN" \
  "https://consul-server-0.secondary/v1/acl/replication?pretty"
```

The primary datacenter always reports ACL replication as disabled even while replication is functioning, so it is not the correct verification target.

## Replace server sets with Autopilot

Enterprise automated upgrades are enabled by default when `DisableUpgradeMigration` is `false`:

```shell
consul operator autopilot get-config
consul operator autopilot set-config -disable-upgrade-migration=false
```

New-version servers initially join as non-voters. When enough have joined to form a quorum, Autopilot promotes them, transfers leadership to the new set, and demotes the old servers. Remove the old servers with `consul leave`. The old and new Consul versions must still support a direct upgrade.

## Tag same-version infrastructure replacements

To replace servers for an image, operating-system, or configuration change without changing the Consul binary, set `UpgradeVersionTag` to a `node_meta` key:

```hcl
node_meta {
  build = "0.0.2"
}
autopilot {
  upgrade_version_tag = "build"
}
```

Autopilot compares the key's semantic versions in `X`, `X.Y`, or `X.Y.Z` form instead of comparing Consul versions. Tag existing servers with the old value and reload them before joining replacement servers with a newer value.
