# Networking, DNS, IPAM, and Firewalls

Use this reference for network creation and attachment, container DNS,
addressing, gateway selection, direct routing, and host firewall integration.

## Network creation and attachment

### Network attachment metadata at container creation (25.0.0)

The long form of `--network` adds `mac-address` and `link-local-ip`, and
`docker run` and `docker container create` accept multiple `--network` flags.
Containers can therefore start with several fully specified attachments instead
of requiring later `network connect` calls.

```console
docker run --network name=frontend,mac-address=02:42:ac:11:00:02 --network name=backend,link-local-ip=169.254.1.10 alpine
```

### Unique network names (25.0.0)

Engine now enforces unique network names, so automation must not rely on
creating multiple networks with the same name.

### Network attachment driver options (27.0.1)

`docker stack deploy` now accepts `driver_opts` on a service's network
attachment. Per-interface sysctls can be supplied through the endpoint driver
option during container creation or network connection; use the `IFNAME`
placeholder because setting an interface such as `eth0` through the
container-wide `--sysctl` form is planned to be rejected.

```console
docker run --network name=mynet,driver-opt=com.docker.network.endpoint.sysctls=net.ipv4.conf.IFNAME.log_martians=1 IMAGE
```

### Reusing macvlan parents (27.0.1)

Multiple macvlan networks may now use the same parent interface, so one parent
can back independently configured macvlan networks.

### Explicit default-gateway selection (28.0.0)

Network attachments accept `gw-priority`; the highest value selects the
container's default gateway, with equal priorities resolved by network-name
order. On `docker run`, it is available through extended `--network` syntax.

```console
docker run --network=name=frontend --network=name=egress,gw-priority=100 IMAGE
```

### Container interface naming (28.0.0)

Linux built-in network drivers accept endpoint option
`com.docker.network.endpoint.ifname` to choose the container-side interface
name. Avoid names that can collide with auto-generated `ethN` devices because
multi-network attachment order is not guaranteed.

```console
docker run --network=name=bridge,driver-opt=com.docker.network.endpoint.ifname=en0 IMAGE
```

## MAC addresses and interface addressing

### Container MAC persistence and repair (26.0.0)

Generated MAC addresses are no longer restored across a restart, while
explicitly configured MAC addresses are preserved. Containers created by Engine
25.0.0 may have duplicate MACs and must be re-created; containers created by
25.0.0 or 25.0.1 with configured MACs must also be re-created if they were
started by 25.0.2 and received generated addresses.

### Randomized interface addresses (28.0.0)

Bridge and macvlan container interfaces now receive randomly generated MAC
addresses and send gratuitous ARP or Neighbor Advertisement messages at
startup. IPv6 addresses on the default bridge are now assigned by IPAM instead
of being derived from the MAC address.

## IPv6 activation and allocation

### IPv6 network activation and overlay transport (25.0.0)

Supplying an IPv6 subnet now automatically enables IPv6 for that network.
Overlay networks can also use IPv6 transport.

### IPv6 on the container loopback interface (26.0.0)

Engine now attempts to enable IPv6 on every container's loopback interface, so
even an IPv4-only container normally has `::1`; IPv6 entries are omitted from
`/etc/hosts` when IPv6 cannot be enabled. Disable it explicitly when required.

```console
docker run --sysctl net.ipv6.conf.all.disable_ipv6=1 IMAGE
```

### Automatic IPv6 address allocation (27.0.1)

Creating a bridge with `--ipv6` and no IPv6 subnet now uses a host-derived ULA
prefix automatically when no IPv6 default pool was configured, and IPv6 entries
in `default-address-pools` may be any size. IPv6 can be enabled for every custom
bridge with the following daemon setting; `DOCKER_ALLOW_IPV6_ON_IPV4_INTERFACE`
no longer has any effect.

```json
{
  "default-network-opts": {
    "bridge": {"com.docker.network.enable_ipv6": "true"}
  }
}
```

### IPv4-free networks (28.0.0)

`docker network create --ipv4=false` disables IPv4 address assignment. A
user-defined bridge must retain IPv4 or IPv6, the default bridge cannot disable
IPv4, and Windows and Swarm networks do not support this setting; macvlan and
ipvlan can disable either or both address families.

```console
docker network create --ipv6 --ipv4=false v6-only
```

### Expanded IPv6 daemon and IPAM configuration (28.0.0)

The daemon's `--ipv6` or `"ipv6": true` setting no longer requires
`fixed-cidr-v6`, and IPAM supports IPv6 subnets larger than `/64`. IPv6 loopback
is also treated as an insecure-registry address by default.

### Dual-stack `host-gateway` (28.0.0)

When the default bridge has IPv6, `host-gateway` produces both IPv4 and IPv6
`/etc/hosts` entries. Two `--host-gateway-ip` values may override them, or
daemon configuration can provide both through `host-gateway-ips`.

```json
{
  "host-gateway-ips": ["192.0.2.1", "2001:db8::1111"]
}
```

## DNS and host mappings

### Stack-deploy host mappings (26.0.0)

Compose files passed to `docker stack deploy` now accept `=` as the separator
in host mappings and accept bracketed IPv6 addresses.

```yaml
services:
  app:
    image: alpine
    extra_hosts:
      - "example=[2001:db8::10]"
```

### Rootless host-loopback access (26.0.0)

Rootless containers can opt into reaching the host at `10.0.2.2` by setting
`DOCKERD_ROOTLESS_ROOTLESSKIT_DISABLE_HOST_LOOPBACK=false`; its default remains
`true`.

```console
export DOCKERD_ROOTLESS_ROOTLESSKIT_DISABLE_HOST_LOOPBACK=false
```

### Container DNS isolation and IPv6 upstreams (26.0.0)

DNS requests from a container attached only to an internal network are no
longer forwarded externally when the host resolver uses a loopback address such
as `127.0.0.53`. Host IPv6 nameservers are now used as upstreams by Engine's
internal DNS instead of being copied into the container's `resolv.conf`.

### Host resolver behavior (28.0.0)

Nameservers from the host's `/etc/resolv.conf` are now contacted from the host
network namespace. If that file has no nameservers and there is no `--dns`
override, Docker no longer falls back to Google DNS except for the default
bridge and build containers.

### Legacy-link and resolver persistence (engine-release-history)

Legacy links no longer inject their environment variables automatically;
temporarily restore them by starting the daemon with
`DOCKER_KEEP_DEPRECATED_LEGACY_LINKS_ENV_VARS=1`. From Engine 29.1, a
user-modified container `/etc/resolv.conf` is preserved across container
restarts.

## Gateway and IPAM allocation

### IPAM validation and legacy-network repair (25.0.0)

Network creation now validates IPAM configuration. Engine also repairs networks
from older releases whose `--ip-range` is larger than their `--subnet`.

### Optional gateway allocation (28.0.0)

Engine no longer reserves a gateway address when none is needed for inhibited
internal bridges, parentless macvlan or ipvlan networks, and L3 ipvlan modes. A
custom network driver can advertise `GwAllocChecker` and decline gateway
allocation after inspecting the network options.

### Network gateway and IPAM allocation changes (engine-release-history)

Macvlan and IPvlan L2 networks no longer receive a default gateway unless IPAM
explicitly supplies `--gateway`. A requested subnet can use an unspecified
address to select only its prefix size from the default pools, and containers
can now request a specific IP even when the network was not created with an
explicit subnet.

```console
docker network create --subnet 0.0.0.0/24 --subnet ::/96 pooled
```

## Bridge gateway modes and direct routing

### Routed bridge gateway mode (27.0.1)

Bridge networks gain `com.docker.network.bridge.gateway_mode_ipv6=<nat|routed>`
and the corresponding IPv4 option. `routed` installs no NAT or masquerading for
published ports, so the surrounding network must route container addresses to
the host; routed-only mappings accept only `0.0.0.0` or `::` and no host port,
and additional host firewall rules may be needed to limit remote access.

```console
docker network create --ipv6 -o com.docker.network.bridge.gateway_mode_ipv6=routed mynet
```

When firewalld is active, Docker creates a `docker-forwarding` policy allowing
forwarding from any zone to the `docker` zone.

### Dual-stack port allocation (27.0.1)

For a mapping without an explicit host port, or one using a host-port range,
Engine now chooses the same available port for IPv4 and IPv6. Container
creation fails if no one port is available on every required address.

### Direct-routing hardening (28.0.0)

Remote direct access to unpublished container ports is now blocked; publish
required ports or deliberately use `nat-unprotected` when that exposure is
intended. Security fixes also prevent remote direct access to published
container ports and neighboring hosts from reaching ports published on a host
loopback address.

### Additional bridge gateway modes (28.0.0)

Bridge networks add `nat-unprotected`, which performs NAT without per-port
filtering and therefore permits direct routing to every container port. An
internal network can use `isolated`, which leaves its bridge without a host
address; `routed` networks are now reachable from other bridge networks on the
same host as well as externally.

```console
docker network create --internal -o com.docker.network.bridge.gateway_mode_ipv4=isolated private
```

## Host firewall ownership

### Encrypted-overlay firewall responsibility (25.0.0)

The daemon no longer appends permissive rules to the end of the host `INPUT`
chain for encrypted overlay networks. Hosts with a restrictive firewall may
need an explicit rule permitting incoming encrypted overlay traffic.

### IPv6 firewalling by default (27.0.1)

`ip6tables` is stable and enabled by default for Linux bridge networks. On
IPv6-enabled bridges this restricts external access to published ports and
enables outbound masquerading; set `"ip6tables": false` only to restore the old
unfiltered behavior, and note that a host with nonfunctional `ip6tables` cannot
create IPv6 networks while it is enabled.

### Bridge-firewall upgrade requirements (28.0.0)

Linux hosts now need kernel `ipset` support, and Engine 28 substantially changes
the iptables and ip6tables rules used for publishing and isolation. Downgrading
requires removing the new rules before starting the older daemon; rebooting is
the documented simplest cleanup.

### IPv6 forwarding policy ownership (28.0.0)

Docker sets the ip6tables `FORWARD` policy to `DROP` only when Docker itself
enables IPv6 forwarding. If the host enables forwarding independently, the
administrator must set an appropriate forwarding policy rather than relying on
Docker to secure it.

### SCTP checksum compatibility (28.0.0)

Docker no longer installs its iptables mangle rule for SCTP checksums. Set
`DOCKER_IPTABLES_SCTP_CHECKSUM=1` in the daemon environment as a temporary
compatibility switch if that rule is still required.

### Experimental nftables firewall backend (engine-release-history)

Engine 29 can use the experimental `nftables` firewall backend. It does not
enable host IP forwarding: if a bridge needs forwarding while it is disabled,
daemon startup or network creation fails; `--ip-forward=false` bypasses the
check, but features such as port forwarding may not work. Dynamically linked
daemons also require libnftables.

```json
{"firewall-backend": "nftables"}
```

### Bridge firewall and routing changes (engine-release-history)

The daemon adds `--bridge-accept-fwmark` to exempt marked packets from Docker's
bridge drop rules. Engine 29 removes the `DOCKER-ISOLATION-STAGE-1` and
`DOCKER-ISOLATION-STAGE-2` chains, permits additional cross-network access
through published host ports and `nat-unprotected` networks, and makes published
ports on routed networks reachable even when that network is not the
container's default route.

The `DOCKER_IPTABLES_SCTP_CHECKSUM` compatibility switch from Engine 28 now has
no effect because the SCTP checksum rule has been removed entirely.
