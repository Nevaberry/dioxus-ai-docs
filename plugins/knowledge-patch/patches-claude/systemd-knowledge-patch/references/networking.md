# Network Configuration

## Forwarding, VLANs, and NAT

### Per-family forwarding and authoritative VLANs (256)

Replace deprecated `IPForward=` with `IPv4Forwarding=` and
`IPv6Forwarding=`, globally or per link. `IPv6SendRA=` and `IPMasquerade=`
imply only their link's forwarding. Once `[BridgeVLAN]` has a valid setting,
networkd removes every VLAN ID not declared there.

```ini
[Network]
IPv4Forwarding=yes
IPv6Forwarding=yes
```

### Nftables-only NAT (259)

Networkd and nspawn no longer create NAT through iptables/libiptc; nftables is
required, and `-Dlibiptc=` is deprecated.

## Configuration ownership and persistence

### Credentials and udev ownership (256)

`systemd-network-generator` can obtain `.network`, `.netdev`, `.link`, and
`networkd.conf` from credentials; networkd can read WireGuard secrets from
credentials. Shipped networkd-only link policies set
`ID_NET_MANAGED_BY=io.systemd.Network`; `.link` files can set, import, or unset
udev properties.

### Dynamic-state retention and reload (257)

Use `KeepConfiguration=dynamic` or `dynamic-on-stop`; `dhcp` and
`dhcp-on-stop` are obsolete. The modes cover DHCPv4, DHCPv6, NDISC, and IPv4LL
with ACD, while networkd restart preserves dynamic state regardless.
`networkctl reload` updates traffic control and mutable netdev settings;
immutable settings such as VLAN ID require recreation.

### Alternative names and preserved MACs (257, 258.10-261.2)

`99-default.link` includes `mac` in `AlternativeNamesPolicy=`, producing
`enx*` alternatives from hardware MACs. Systemd no longer replaces a MAC
already assigned by userspace.

## Addressing, bridges, and DHCP

### IPv6 labels and bridge capacity (257)

Global `[IPv6AddressLabel]` entries define `Prefix=` and `Label=`. Bridges use
`FDBMaxLearned=` to cap dynamic entries; `MulticastGroupAddress=` accepts L2
and L3 MDB entries.

### Protocol and lease persistence controls (258)

IPv4 duplicate-address detection defaults to 200ms and is configurable with
`IPv4DuplicateAddressDetectionTimeoutSec=`. `ClientIdentifier=` may be global;
DHCP-server `PersistLeases=runtime` retains leases at runtime. Additions include
DHCPv6 `UseSIP=`, `MPLSRouting=`, DHCPv4 `BOOTP=`, tunnel `Local=dhcp_pd`,
HSR/SRP netdevs, and further bridge/VXLAN controls.

### DHCP domains and hostnames (259)

DHCP server supports `EmitDomain=` and `Domain=`, and individual static leases
support `Hostname=`. `resolvectl --json=` exposes resolved's complete
`DumpDNSConfiguration()` result.

## Cellular, routes, and link offloads

### MobileNetwork (260)

`[MobileNetwork]` drives ModemManager simple-connect. Configure APN,
authentication and credentials, IP family, roaming, PIN, operator, route
metric, and gateway behavior.

```ini
[MobileNetwork]
APN=internet.example
AllowRoaming=no
```

### ECMP and offloads (260)

`MultiPathRoute=` supports interface-bound ECMP. `.link` files configure
`ScatterGather=`, `ScatterGatherFragmentList=`,
`TCPECNSegmentationOffload=`, `TCPMangleIdSegmentationOffload=`,
`GenericReceiveOffloadList=`, and
`GenericReceiveOffloadUDPForwarding=`.

### Link state over Varlink (260)

`io.systemd.Network.Link.Up()` and `Down()` back `networkctl up` and `down`.
Networkd Varlink/JSON returns IP addresses as readable strings in addition to
the existing integer arrays.

## DNS and online readiness

### DNS-aware wait and delegated zones (258)

`systemd-networkd-wait-online --dns` waits for resolved configuration.
`RefuseRecordTypes=` blocks chosen RR types. Files in
`/etc/systemd/dns-delegate.d/*.dns-delegate` create domain-specific scopes
with servers and routing/search domains.

### Scoped delegated and NSS traffic (260)

Delegate files accept `FirewallMark=`. `SYSTEMD_NSS_RESOLVE_INTERFACE`
restricts an nss-resolve lookup to an interface, and ifindex 0 in
`BrowseServices` browses all mDNS interfaces.

### Strict per-link DNS-over-TLS (258.10-261.2)

In v259.8, v260.4, and v261.2, per-link `DNSOverTLS=yes` performs certificate
verification. Connections with invalid or mismatched server certificates now
fail.
