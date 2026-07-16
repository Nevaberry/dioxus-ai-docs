# Networking

Consult this reference for DNS, DHCP, early networking, NetworkManager, Nmstate, routing, packet filtering, transport behavior, and network-device controls.

## Contents

- [Name resolution, DHCP, and early networking](#name-resolution-dhcp-and-early-networking)
- [NetworkManager and Nmstate profiles](#networkmanager-and-nmstate-profiles)
- [Firewalls, nftables, and diagnostics](#firewalls-nftables-and-diagnostics)
- [Routing, transport, and device interfaces](#routing-transport-and-device-interfaces)

## Name resolution, DHCP, and early networking

### Resolver, DHCP, printing, and mail transitions (10.0)

`systemd-resolved` is supported except for its DNSSEC validation, while `dnsconfd` configures local caching, split DNS, and DNS over TLS. Kea replaces ISC DHCP; CUPS follows system crypto policy unless `SSLOptions NoSystem` opts out; Postfix defaults to LMDB because Berkeley DB is absent and existing BDB maps must be converted.

### System-wide encrypted DNS (10.1)

DNS over TLS is now generally available for both early boot and installed systems, using NetworkManager's `dnsconfd` plugin and Unbound with policies that can forbid plaintext fallback. A custom CA for installation-time DoT can be supplied only through Kickstart `%certificate`, and early boot also needs the relevant kernel arguments.

### Per-interface forwarding and firmware-provided networking (10.1)

NetworkManager profiles and Nmstate can set `ipv4.forwarding`; `auto` enables it for shared connections and otherwise follows the kernel default. `nm-initrd-generator` now parses NBFT firmware data directly to create early-boot network and NVMe/TCP connections, replacing dracut's `95nvmf` path.

### DNSSEC provider and policy transition (10.1)

`named` and the `dnssec` utilities regain hardware-token access through OpenSSL providers, restoring provider-backed zone signing. BIND's `auto-dnssec` is deprecated; migrate to a `dnssec-policy` Key and Signing Policy.

### Interface identity and early DHCP (10.2)

Nmstate can add or remove interface `alt-names`. The `rd.net.dhcp.client-id=` kernel argument supplies a DHCP client identifier during early boot.

### Corrected NetworkManager and DNS behavior (10.2)

`sriov.vfs` supports `reapply` when the total VF count is unchanged, NetworkManager clients can set a global DNS search domain without a DNS server, and `nmstate.service` now only `Wants` rather than `Requires` `NetworkManager-wait-online.service`. Unbound delegates TLS protocol selection to crypto policies, so `LEGACY` can permit TLS 1.2 and 1.1.


## NetworkManager and Nmstate profiles

### Nmstate route and interface selection (10.1)

Nmstate routes add `mtu` and `quickack`, and `next-hop-interface` can name a profile bound by MAC address rather than a volatile interface name. Interfaces can be selected by PCI address, and VLANs gain ingress and egress priority maps.

### Nmstate FEC, bonds, and delegated prefixes (10.1)

Nmstate can configure `RS-FEC`, `Base-R`, or disabled FEC, plus bond `lacp_active` and `ns_ip6_target`. NetworkManager can pin subnet IDs for IPv6 prefix-delegation downstreams, and `NetworkManager-libreswan` profiles can set `no-nm-default=true` to retain Libreswan defaults, including subnet-to-subnet configurations.

### Libreswan behavior through Nmstate (10.2)

Set `nm-auto-defaults: false` in Nmstate YAML to stop NetworkManager from injecting its defaults and retain Libreswan's own defaults; compatibility keeps this setting `true` by default. A NetworkManager-Libreswan profile with `nm-connect-mode=ondemand` remains listening after an unreachable peer prevents initial activation.


## Firewalls, nftables, and diagnostics

### Packet-filtering and network interfaces (10.0)

firewalld adds `StrictForwardPorts` (default `no`); setting it to `yes` blocks DNAT traffic, including container-published ports, unless explicitly allowed. Nftables adds VLAN/Q-in-Q matching and egress hook listing, the kernel supports BPF-oriented `netkit` devices, Nmstate can enforce Libreswan SAN validation, and i40e adds the `mdd-auto-reset-vf` private flag for automatically recovering a VF after malicious-driver detection.

### Network diagnostics and locked-down firmware access (10.1)

`nft monitor trace` now includes connection-tracking state, and new packet-drop reasons plus `LINUX_MIB_PAWS_TW_REJECTED` and `LINUX_MIB_PAWS_OLD_ACK` improve diagnostics. The kernel's `fwctl` RPC interface lets tools such as `mstflint` access device firmware under kernel lockdown.

### Dynamic nftables hooks and policy sets (10.2)

Nftables `netdev` hooks and flowtables can bind absent interfaces by name or suffix wildcard, become active when matching interfaces appear, and can be inspected with `nft list hooks`. Firewalld adds reusable policy sets such as `gateway`, while nftables also adds flowtable monitoring, protocol values in sets, `queue` types, MPTCP subtype names, map deletion by handle, and JSON `typeof`.


## Routing, transport, and device interfaces

### Iproute 6.14 interfaces (10.1)

New interfaces include 16-bit `ip nexthop` weights, `ip monitor maddress`, DSCP and flow-label selectors in `ip rule`, IPv6 flow labels in `ip route`, `down` filters for address/link display, RDMA event monitoring, and vDPA MAC assignment. `tc flower` can match tunnel metadata and `tc` gains TSN Hold/Release support.

### KTLS TLS 1.3 boundaries (10.1)

The Technology Preview kTLS implementation can rekey TLS 1.3 sessions in-kernel, allowing long-lived transfers when the userspace TLS library cooperates. TLS 1.3 still cannot be offloaded to NICs, and TLS 1.2 renegotiation is not covered by this rekeying support.

### Fully supported redundant Ethernet (10.2)

PRP and HSR move from preview to full support, NetworkManager adds `hsr.interlink` for RedBox configurations, and VLAN interfaces can sit above HSR or PRP while supervision frames remain untagged.

### Network transport and device controls (10.2)

`tcp_rto_max_ms` and the higher-priority `TCP_RTO_MAX_MS` socket option can lower the 120000-ms TCP retransmission ceiling. RHEL 10.2 also supports Wi-Fi 7, supplies a `dpll` management utility, and defaults the `e1000e` `disable-k1` private flag on for Meteor Lake and later systems; use `ethtool --set-priv-flags DEVICE disable-k1 on` on older affected systems.

### Iproute 6.17 interfaces (10.2)

Iproute adds 64-bit `tc` hardware counters, `ip rule` port and DSCP masks, bridge VLAN statistics, VXLAN multicast routing, `ip neigh extern_valid`, and FDB activity notifications.

