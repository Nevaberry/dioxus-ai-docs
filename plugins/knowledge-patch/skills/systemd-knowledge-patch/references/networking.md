# Network Configuration

## Configure forwarding and bridge VLANs

- `IPForward=` is deprecated. Use `IPv4Forwarding=` and `IPv6Forwarding=` globally or per link. `IPv6SendRA=` and `IPMasquerade=` imply only per-link forwarding (since 256).

```ini
[Network]
IPv4Forwarding=yes
IPv6Forwarding=yes
```

- Once a `[BridgeVLAN]` section contains any valid setting, networkd removes every VLAN ID on that interface that is not declared in the section (since 256).
- Bridges support `FDBMaxLearned=` to cap dynamically learned forwarding entries. `MulticastGroupAddress=` accepts layer-2 and layer-3 MDB entries (since 257).

## Supply network configuration and ownership

- `systemd-network-generator` can read `.network`, `.netdev`, `.link`, and `networkd.conf` content from system credentials. Networkd can obtain WireGuard secrets from credentials (since 256).
- Shipped networkd-only link policies set `ID_NET_MANAGED_BY=io.systemd.Network`. A `.link` file can set, import, or unset udev properties explicitly (since 256).
- In 258, Tun/Tap `User=` and `Group=` were restricted to system accounts; that restriction was partially reverted in 260 and may be backported to 259.

## Preserve and reload dynamic state

- `KeepConfiguration=dynamic` and `dynamic-on-stop` replace `dhcp` and `dhcp-on-stop`; they cover DHCPv4, DHCPv6, NDISC, and IPv4LL with ACD. A networkd restart preserves dynamic state regardless of this option (since 257).
- `networkctl reload` applies traffic-control and mutable `.netdev` changes in place. Immutable settings such as a VLAN ID still require interface recreation (since 257).
- The shipped `99-default.link` adds `mac` to `AlternativeNamesPolicy=`, producing an `enx*` alternative name from a hardware-assigned MAC even when another primary naming policy wins (since 257).

## Configure addresses, routes, and protocols

- Global `networkd.conf` supports `[IPv6AddressLabel]` with `Prefix=` and `Label=` for source-address labels (since 257).
- IPv4 duplicate-address detection defaults to 200ms rather than 7s and is configurable with `IPv4DuplicateAddressDetectionTimeoutSec=` (since 258).
- Global `ClientIdentifier=` configures the DHCP client. A DHCP server can set `PersistLeases=runtime` to retain leases in runtime storage (since 258).
- Added protocol controls include DHCPv6 `UseSIP=`, `MPLSRouting=`, DHCPv4 `BOOTP=`, tunnel `Local=dhcp_pd`, HSR/SRP netdevs, and additional bridge and VXLAN settings (since 258).
- `MultiPathRoute=` supports interface-bound ECMP routes (since 260).
- `.link` supports `ScatterGather=`, `ScatterGatherFragmentList=`, `TCPECNSegmentationOffload=`, `TCPMangleIdSegmentationOffload=`, `GenericReceiveOffloadList=`, and `GenericReceiveOffloadUDPForwarding=` (since 260).

## Serve DHCP and cellular links

- The DHCP server supports `EmitDomain=` and `Domain=`, and an individual static lease supports `Hostname=` (since 259).
- `[MobileNetwork]` uses ModemManager's simple-connect protocol. It configures APN, authentication, credentials, IP family, roaming, PIN, operator, route metric, and gateway use (since 260).

```ini
[MobileNetwork]
APN=internet.example
AllowRoaming=no
```

## Use socket and activation networking

- Socket units select Multipath TCP with `SocketProtocol=mptcp`. Per-connection AF_UNIX stream services receive the peer address in `REMOTE_ADDR` (since 257).
- `BindNetworkInterface=` binds every socket created for a service to a named interface, including a VRF (since 260).
- Networkd and nspawn use nftables exclusively for NAT; iptables/libiptc setup was removed (since 259).

## Control networkd over Varlink

- `io.systemd.Network.Link.Up()` and `Down()` back `networkctl up` and `down` (since 260).
- Networkd Varlink and JSON address data includes a human-readable address string alongside the existing integer array, allowing parsers to migrate compatibly (since 260).

## Name interfaces predictably

- DeviceTree aliases and `firmware_node/sun` contribute to interface names; DeviceTree Wi-Fi gained predictable names, and MCTP uses the `mc` prefix (since 257, 259, and 260).
