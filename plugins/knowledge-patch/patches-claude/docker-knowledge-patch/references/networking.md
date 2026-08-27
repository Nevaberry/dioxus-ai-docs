# Networking, DNS, IPAM, and Firewalls

## Create-time network attachments

Engine 25.0.0 lets `docker run` and `docker container create` repeat the
long-form `--network` flag. Each attachment can set `mac-address` and
`link-local-ip`, avoiding a later `network connect`.

```console
docker run \
  --network name=frontend,mac-address=02:42:ac:11:00:02 \
  --network name=backend,link-local-ip=169.254.1.10 alpine
```

Since 26.0.0, Compose files used by `docker stack deploy` accept `=` in
`extra_hosts` mappings and bracketed IPv6 addresses.

```yaml
services:
  app:
    image: alpine
    extra_hosts:
      - "example=[2001:db8::10]"
```

Engine 27.0.1 adds attachment `driver_opts` to `docker stack deploy` and
endpoint sysctls to container create/connect. Use the `IFNAME` placeholder;
container-wide sysctls naming `eth0` are not a durable substitute.

```console
docker run --network name=mynet,driver-opt=com.docker.network.endpoint.sysctls=net.ipv4.conf.IFNAME.log_martians=1 IMAGE
```

Engine 28.0.0 adds `com.docker.network.endpoint.ifname` for Linux built-in
drivers. Do not choose a name that may collide with generated `ethN` devices;
attachment order is not stable.

```console
docker run --network=name=bridge,driver-opt=com.docker.network.endpoint.ifname=en0 IMAGE
```

### Default gateway selection

Engine 28.0.0 attachment option `gw-priority` selects the default gateway. The
highest number wins; a tie is resolved by network-name order.

```console
docker run --network=name=frontend --network=name=egress,gw-priority=100 IMAGE
```

## Network identity and addresses

### Names and MAC addresses

Engine 25.0.0 enforces unique network names. Engine 28.0.0 randomizes MACs on
bridge and macvlan container interfaces and sends gratuitous ARP or Neighbor
Advertisement at startup. Default-bridge IPv6 addresses are allocated by IPAM
rather than derived from MACs.

Multiple macvlan networks may share a parent interface since 27.0.1.

### IPAM validation and allocation

Engine 25.0.0 validates IPAM at network creation and repairs older networks
whose `--ip-range` exceeds their `--subnet`.

Engine 28.0.0 can omit a gateway for inhibited internal bridges, parentless
macvlan/ipvlan, and L3 ipvlan. Custom drivers can advertise `GwAllocChecker`
and decline the allocation after reading network options.

In Engine 29, macvlan and ipvlan L2 networks receive no default gateway unless
IPAM supplies `--gateway`. An unspecified subnet address requests only a prefix
size from default pools, and a container can request a fixed IP even if the
network lacks an explicit subnet.

```console
docker network create --subnet 0.0.0.0/24 --subnet ::/96 pooled
```

## IPv6 and address families

### Enabling IPv6

Since 25.0.0, supplying an IPv6 subnet enables IPv6 automatically; overlay
networks can use IPv6 transport. Engine 27.0.1 can automatically allocate a
host-derived ULA prefix for `--ipv6` when no subnet or IPv6 default pool is
configured. IPv6 default pools can use any prefix size.

Enable IPv6 on every custom bridge with:

```json
{
  "default-network-opts": {
    "bridge": {"com.docker.network.enable_ipv6": "true"}
  }
}
```

`DOCKER_ALLOW_IPV6_ON_IPV4_INTERFACE` no longer has an effect. Since 28.0.0,
daemon `--ipv6` does not require `fixed-cidr-v6`, IPAM accepts IPv6 networks
larger than `/64`, and IPv6 loopback counts as an insecure-registry address.

### Loopback inside containers

Engine 26.0.0 tries to enable IPv6 on every container loopback, including an
otherwise IPv4-only container, so `::1` is normally present. If enablement
fails, IPv6 `/etc/hosts` entries are omitted. Disable it deliberately when
needed:

```console
docker run --sysctl net.ipv6.conf.all.disable_ipv6=1 IMAGE
```

### IPv4-free networks

Engine 28.0.0 adds `docker network create --ipv4=false`. A custom bridge must
retain IPv4 or IPv6; the default bridge cannot disable IPv4. Windows and Swarm
do not support the option. Macvlan and ipvlan may disable one or both families.

```console
docker network create --ipv6 --ipv4=false v6-only
```

### Dual-stack ports and host gateway

Since 27.0.1, an implicit host port or host-port range chooses the same port
for IPv4 and IPv6. Creation fails if no common port is free.

Since 28.0.0, an IPv6 default bridge makes `host-gateway` add both IPv4 and
IPv6 host entries. Override them with two `--host-gateway-ip` values or:

```json
{"host-gateway-ips": ["192.0.2.1", "2001:db8::1111"]}
```

## DNS and resolver behavior

Engine 26.0.0 stops forwarding DNS externally for a container attached only to
an internal network even when the host resolver points to a loopback stub such
as `127.0.0.53`. Host IPv6 nameservers become upstreams of Docker's internal
DNS instead of entries copied directly into the container.

Engine 28.0.0 contacts host `/etc/resolv.conf` nameservers from the host network
namespace. If no nameserver and no `--dns` exist, public Google DNS fallback
remains only for default-bridge and build containers. Engine 29.1 preserves a
user-modified container `/etc/resolv.conf` across restart.

## Bridge gateway modes

### Routed networks

Engine 27.0.1 adds IPv4/IPv6 gateway mode `routed`. It installs no NAT or
masquerading, so the surrounding network must route container prefixes to the
host. Routed-only published mappings accept only `0.0.0.0` or `::` and no host
port. Apply host firewall policy explicitly.

```console
docker network create --ipv6 -o com.docker.network.bridge.gateway_mode_ipv6=routed mynet
```

When firewalld is active, Docker creates a `docker-forwarding` policy allowing
forwarding from any zone into the `docker` zone.

### Unprotected and isolated modes

Engine 28.0.0 adds `nat-unprotected`, which performs NAT without per-port
filtering and permits direct routing to every container port. An internal
network can use `isolated`, leaving the bridge without a host address. Routed
networks also become reachable from other local bridge networks.

```console
docker network create --internal \
  -o com.docker.network.bridge.gateway_mode_ipv4=isolated private
```

## Firewall transitions

### Encrypted overlays

Since 25.0.0, Docker no longer appends a permissive encrypted-overlay rule to
the end of host `INPUT`. Restrictive hosts must explicitly allow incoming
encrypted overlay traffic.

### IPv6 filtering

Engine 27.0.1 makes `ip6tables` stable and enabled by default. IPv6 bridges
therefore filter inbound access to published ports and masquerade outbound
traffic. Set `"ip6tables": false` only to restore unfiltered legacy behavior;
an enabled but nonfunctional ip6tables prevents creation of IPv6 networks.

Engine 28.0.0 sets the IPv6 `FORWARD` policy to `DROP` only when Docker itself
enables forwarding. If the host enables forwarding, the administrator owns the
policy.

### Engine 28 rules and direct routing

Engine 28.0.0 requires kernel `ipset` and substantially changes iptables and
ip6tables publishing/isolation rules. Remove those rules before downgrade; a
reboot is the documented simplest cleanup.

Remote direct access to unpublished ports is blocked. Security fixes also
block remote direct access to published container ports and access from
neighboring hosts to ports published on host loopback. Publish required ports
or choose `nat-unprotected` only when universal direct routing is intentional.

### Engine 29 rules and nftables

Engine 29 removes `DOCKER-ISOLATION-STAGE-1` and `-STAGE-2`, allows more
cross-network access through host-published ports and `nat-unprotected`, and
makes routed-network published ports reachable even when that network is not
the default route. `--bridge-accept-fwmark` exempts marked packets from bridge
drop rules.

The experimental nftables backend requires libnftables for dynamically linked
daemons and does not enable host forwarding. If a bridge requires forwarding
while it is off, startup or network creation fails. `--ip-forward=false`
bypasses the check but can break port forwarding. Configure host forwarding
yourself.

```json
{"firewall-backend": "nftables"}
```

## Legacy links and remote exposure

Engine 29 stops injecting environment variables for legacy links by default.
`DOCKER_KEEP_DEPRECATED_LEGACY_LINKS_ENV_VARS=1` temporarily restores them.
Default-bridge `--link` remains deprecated and is targeted for removal in
Engine 30; Engine 29.6 warns. Move services to custom networks. Links on
non-default networks remain supported.

Non-local daemon TCP with explicit `--tls=false` or `--tlsverify=false` fails
from Engine 27. Use verified TLS, a Unix socket, or SSH; `tcp://localhost` is
exempt.

## Validation matrix

After upgrades, test published and unpublished ports from the host, a neighbor,
a remote routed host, and another Docker network. Repeat for host-loopback
bindings, IPv4, IPv6, NAT, routed, `nat-unprotected`, and internal/isolated
networks. Inspect routes, IPAM allocations, firewall backend, forwarding policy,
and resolver persistence rather than relying on old defaults.
