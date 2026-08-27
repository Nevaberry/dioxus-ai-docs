# Network Configuration

## Forwarding, VLANs, and NAT

### Per-family forwarding and authoritative bridge VLANs (256)

Replace deprecated `IPForward=` with per-link or global
`IPv4Forwarding=`/`IPv6Forwarding=`. `IPv6SendRA=` and `IPMasquerade=` imply
only their per-link settings. Once `[BridgeVLAN]` has a valid setting,
networkd removes every undeclared VLAN ID from that interface.

### Nftables-only NAT (259)

Networkd and nspawn no longer create NAT through iptables/libiptc. Provide
nftables; `-Dlibiptc=` is deprecated.

## Configuration sources and link ownership

### Credentials and udev properties (256)

Network generator can read `.network`, `.netdev`, `.link`, and
`networkd.conf` from system credentials; networkd reads WireGuard secrets
from credentials. Shipped networkd-only policies set
`ID_NET_MANAGED_BY=io.systemd.Network`, and `.link` can set/import/unset udev
properties.

### Dynamic state and reload (257)

Use `KeepConfiguration=dynamic` or `dynamic-on-stop` instead of `dhcp` or
`dhcp-on-stop`; these cover DHCPv4/v6, NDISC, and IPv4LL with ACD. Restart
preserves dynamic state regardless. `networkctl reload` updates traffic
control and mutable netdev settings, but immutable identifiers such as VLAN ID
require deletion/recreation.

### MAC alternative names and preservation (257, 258.10-261.2)

Default `99-default.link` adds `mac` to `AlternativeNamesPolicy=`, producing
`enx*` alternatives for hardware-assigned MACs. All covered point releases
preserve a MAC already set by userspace rather than regenerating it.

## DHCP, routing, and bridges

### IPv6 labels and bridge limits (257)

Global `[IPv6AddressLabel]` sections set `Prefix=` and `Label=`. Bridges use
`FDBMaxLearned=` to cap learned entries; `MulticastGroupAddress=` accepts L2
and L3 MDB entries.

### Protocol and persistence additions (258)

IPv4 DAD defaults to 200ms and is configurable with
`IPv4DuplicateAddressDetectionTimeoutSec=`. `ClientIdentifier=` can be global;
DHCP server `PersistLeases=runtime` retains runtime leases. Additions include
DHCPv6 `UseSIP=`, `MPLSRouting=`, DHCPv4 `BOOTP=`, tunnel `Local=dhcp_pd`,
HSR/SRP netdevs, and bridge/VXLAN controls.

### DHCP domains and hostnames (259)

DHCP server `EmitDomain=`/`Domain=` advertises domains, and individual static
leases accept `Hostname=`.

### Cellular links (260)

`[MobileNetwork]` uses ModemManager simple-connect and supports APN,
authentication, credentials, IP family, roaming, PIN, operator, route metric,
and gateway behavior.

### ECMP and offloads (260)

`MultiPathRoute=` supports interface-bound ECMP. `.link` can configure
`ScatterGather=`, `ScatterGatherFragmentList=`,
`TCPECNSegmentationOffload=`, `TCPMangleIdSegmentationOffload=`,
`GenericReceiveOffloadList=`, and
`GenericReceiveOffloadUDPForwarding=`.

## Networkd API and DNS security

### Link state Varlink (260)

`io.systemd.Network.Link.Up()` and `Down()` back `networkctl up/down`.
Networkd Varlink/JSON adds a human-readable IP address string alongside the
existing integer array; parsers should accept both.

### Strict per-link DNS-over-TLS (258.10-261.2)

V259.8, v260.4, and v261.2 honor per-link `DNSOverTLS=yes` certificate
verification. A link can now fail if its server certificate is invalid or
does not match.
