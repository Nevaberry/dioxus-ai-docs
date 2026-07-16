# Networking, DNS, IPAM, and Firewalls

Use this reference for network attachment syntax, address allocation, DNS, bridge gateway modes, routing, and firewall ownership.

## Attach containers and services

- `docker run` and `docker container create` accept repeated `--network` flags (since 25.0.0). Extended syntax accepts `mac-address` and `link-local-ip`:

```console
docker run --network name=NET_A,mac-address=02:42:ac:11:00:02 --network NET_B IMAGE
```

- Stack `extra_hosts` entries accept `=` as the name/address separator and bracketed IPv6 addresses (since 26.0.0):

```yaml
services:
  app:
    image: example
    extra_hosts:
      - "gateway=[2001:db8::1]"
```

- Stack service network attachments accept `driver_opts` (since 27.0.1).
- Multiple macvlan networks can reuse the same parent interface (since 27.0.1).

## DNS and resolver behavior

- A container connected only to an internal network does not forward DNS queries to external resolvers when the host resolver is loopback-based, such as systemd-resolved at `127.0.0.53` (since 26.0.0).
- Docker tries to enable IPv6 on every container loopback, including on IPv4-only networks (since 26.0.0). `::1` appears unless IPv6 cannot be enabled; in that case IPv6 entries are omitted from `/etc/hosts`. Disable it explicitly when necessary:

```console
docker run --sysctl net.ipv6.conf.all.disable_ipv6=1 IMAGE
```

- Host IPv6 nameservers act as upstreams for Docker's internal DNS rather than being copied into container `resolv.conf` (since 26.0.0).
- Nameservers from host `/etc/resolv.conf` are always contacted from the host network namespace (since 28.0.0). If the file contains none and no `--dns` override exists, Docker no longer falls back to Google resolvers except on the default bridge and in build containers.
- Engine 29.1 preserves manual edits to a container's `/etc/resolv.conf` across restart.

## MAC and interface behavior

- Generated MAC addresses are not restored across container restarts, while explicit MAC addresses are preserved (since 26.0.0).
- Recreate containers created by Engine 25.0.0 because they can carry duplicate MACs. Also recreate containers created by 25.0.0 or 25.0.1 with configured MACs if Engine 25.0.2 started them.
- Bridge and macvlan interfaces receive randomized MAC addresses and announce them through gratuitous ARP or Neighbor Advertisement (since 28.0.0). Default-bridge IPv6 addresses come from IPAM instead of being derived from MAC addresses.
- All built-in Linux network drivers accept endpoint option `com.docker.network.endpoint.ifname` (since 28.0.0). Avoid names that can collide with automatically allocated `ethN` interfaces:

```console
docker network connect --driver-opt=com.docker.network.endpoint.ifname=en0 NET CONTAINER
docker run --network=name=NET,driver-opt=com.docker.network.endpoint.ifname=en0 IMAGE
```

## Endpoint sysctls

- Supply per-interface sysctls as endpoint driver option `com.docker.network.endpoint.sysctls` and use `IFNAME` as the interface placeholder (since 27.0.1):

```console
docker run --network name=mynet,driver-opt=com.docker.network.endpoint.sysctls=net.ipv4.conf.IFNAME.log_martians=1 IMAGE
```

- Do not use a container-wide `--sysctl` that names a concrete interface. API v1.48 stops migrating `HostConfig.Sysctls` entries naming `eth0` into endpoint options.

## IPv4, IPv6, and IPAM

- Supplying an IPv6 subnet automatically enables IPv6 on that network, and overlay networks can use IPv6 transport (since 25.0.0).
- Network creation validates IPAM configuration (since 25.0.0). Existing networks with an `--ip-range` broader than `--subnet` are repaired automatically.
- `--ipv6` without an explicit IPv6 subnet allocates a host-derived ULA prefix when daemon default pools are absent or contain no IPv6 pool (since 27.0.1). Configured IPv6 pools may be any size.
- Set IPv6 as the default for every custom bridge with daemon network options:

```json
{
  "default-network-opts": {
    "bridge": { "com.docker.network.enable_ipv6": "true" }
  }
}
```

- Daemon `--ipv6` or `"ipv6": true` no longer requires `fixed-cidr-v6` (since 28.0.0), and IPAM accepts IPv6 pools broader than `/64`.
- `docker network create --ipv4=false` disables IPv4 assignment (since 28.0.0):

```console
docker network create --ipv6 --ipv4=false v6-only
```

  User-defined bridges must enable at least IPv4 or IPv6. The default bridge, Windows networks, and Swarm networks cannot disable IPv4. Macvlan and ipvlan may disable either or both families.
- A network can request only a prefix size from daemon default pools with unspecified subnets such as `--subnet 0.0.0.0/24 --subnet ::/96`. Older Engines cannot use such a network after downgrade; delete and recreate it.
- `DOCKER_ALLOW_IPV6_ON_IPV4_INTERFACE` no longer has any effect (since 27.0.1). Enable network IPv6 explicitly with `--ipv6`.

## Default gateways and endpoint priorities

- `docker run`, `docker container create`, and `docker network connect` accept `gw-priority` (since 28.0.0). The endpoint with the largest value supplies the default gateway; ties use lexicographic network-name order. `docker run` exposes it only in extended network syntax:

```console
docker run --network=name=frontend --network=name=egress,gw-priority=100 IMAGE
```

- A custom driver can advertise `GwAllocChecker` and answer `GwAllocCheckerRequest` to suppress an unnecessary gateway allocation (since 28.0.0).
- Docker no longer reserves a gateway by default for inhibited internal bridges, parentless macvlan/ipvlan networks, or L3 ipvlan modes (since 28.0.0).
- Macvlan and IPvlan-L2 networks no longer receive a default gateway unless IPAM explicitly includes `--gateway`.
- With IPv6 on the default bridge, `host-gateway` creates both IPv4 and IPv6 `/etc/hosts` entries (since 28.0.0). Supply `--host-gateway-ip` twice or configure an address pair:

```json
{"host-gateway-ips":["192.0.2.1","2001:db8::1111"]}
```

## Bridge gateway modes and direct routing

- Bridge options `com.docker.network.bridge.gateway_mode_ipv4` and `gateway_mode_ipv6` accept `nat` or `routed` starting in 27.0.1.
- `routed` omits NAT and masquerading but opens published ports in the container firewall. The surrounding network must route container addresses through the host.
- A mapping that applies only to routed mode cannot specify a host port and may bind only `0.0.0.0` or `::`:

```console
docker network create --ipv6 -o com.docker.network.bridge.gateway_mode_ipv6=routed mynet
```

- Engine 28.0.0 adds `nat-unprotected`, which retains NAT without per-port filtering, and `isolated`, which is valid for internal networks and leaves the host bridge without an address:

```console
docker network create -o com.docker.network.bridge.gateway_mode_ipv4=nat-unprotected open-net
docker network create --internal -o com.docker.network.bridge.gateway_mode_ipv4=isolated isolated-net
```

- Routed networks can be reached from other bridge networks on the same host (since 28.0.0).
- Engine 28.0.0 blocks remote direct-routed access to unpublished ports. Ports published to a loopback host address are no longer reachable from neighboring hosts. Publish required ports or deliberately use `nat-unprotected`.
- Engine 29 makes published ports on a `routed` bridge reachable even when that bridge is not the container's default gateway.

## Port allocation

- A publication without an explicit host port, or with a host-port range, chooses the same port for IPv4 and IPv6 (since 27.0.1). Container creation fails if no candidate is free on every required address.

## iptables and ip6tables

- For encrypted overlay networks, Docker no longer appends `ACCEPT` rules to the host `INPUT` chain (since 25.0.0). If the firewall blocks overlay traffic, add the required incoming rule yourself.
- `ip6tables` filtering is stable and enabled by default for Linux bridges (since 27.0.1). On IPv6 bridges, only published ports are externally reachable and outgoing traffic is masqueraded.
- Set `"ip6tables": false` or `--ip6tables=false` to restore unfiltered behavior, or keep filtering and configure published ports/direct routing. A daemon with broken host ip6tables starts but cannot create IPv6 networks.
- With firewalld, Docker creates a `docker-forwarding` policy permitting forwarding from any zone to the `docker` zone (since 27.0.1).
- Engine 28.0.0 requires kernel `ipset` support and installs substantially different iptables/ip6tables rules. Remove those rules before downgrading; reboot is the simplest documented cleanup, while flushing the IPv4 and IPv6 filter tables is the broader alternative.
- Docker sets the ip6tables `filter/FORWARD` policy to `DROP` only when Docker itself enables IPv6 forwarding (since 28.0.0). If the host enables forwarding independently, configure a secure forwarding policy yourself.
- Docker no longer installs its SCTP checksum rule in the mangle table (since 28.0.0). `DOCKER_IPTABLES_SCTP_CHECKSUM=1` temporarily restores it, but the switch is scheduled for removal.

## nftables and Engine 29 reachability

- Select the experimental nftables backend with `--firewall-backend=nftables`; `docker info` reports the active backend. Dynamically linked daemons require libnftables:

```console
dockerd --firewall-backend=nftables
```

- Docker does not enable host IP forwarding with nftables. Enable it and secure forwarding between non-Docker interfaces. `--ip-forward=false` bypasses the startup check but can break bridge behavior such as port forwarding.
- `--bridge-accept-fwmark=<mark>` lets marked packets pass bridge drop rules under either iptables or nftables.
- Engine 29 removes `DOCKER-ISOLATION-STAGE-1` and `DOCKER-ISOLATION-STAGE-2`. Without the userland proxy, a container can consequently reach host-published ports for containers on other networks and directly reach containers on other `nat-unprotected` networks. Reassess isolation after upgrade.
