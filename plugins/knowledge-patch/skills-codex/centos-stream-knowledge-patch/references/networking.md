# Networking

## Contents

- [Addressing, routing, and interface management](#addressing-routing-and-interface-management)
- [DHCP, DNS, and time](#dhcp-dns-and-time)
- [IPsec and transport controls](#ipsec-and-transport-controls)
- [nftables and firewalld](#nftables-and-firewalld)
- [Major-version profile migration](#major-version-profile-migration)

## Addressing, routing, and interface management

### `iproute` and DPLL tooling

`iproute` 6.17 adds port and DSCP masks to `ip rule`, bridge VLAN statistics to `ip stats`, FDB activity controls, and new neighbor and VXLAN attributes. The package includes `dpll` for managing and monitoring digital phase-locked-loop devices and pins over netlink. (9.8)

### Fully supported HSR and PRP networking

The kernel's HSR and PRP zero-recovery protocols move from Technology Preview to full support. NetworkManager exposes `hsr.interlink` for RedBox operation. VLAN interfaces can be layered on HSR or PRP interfaces, but supervision frames remain untagged. (9.8)

### Nmstate interface alternative names

Nmstate can add or remove interface alternative names with `alt-names`: (9.8)

```yaml
interfaces:
  - name: enp1s0
    alt-names:
      - name: LAN
```

### Per-interface IPv4 forwarding

NetworkManager and Nmstate control per-connection routing with `ipv4.forwarding`. The default `auto` enables forwarding while any shared connection is active and otherwise follows the kernel default, avoiding a separate per-interface `sysctl`. (9.8)

### Parallel FRRouting versions

The `frr10` AppStream package supplies FRRouting 10 alongside the existing `frr` version 8 package, allowing adoption without replacing version 8. (9.8)

### Stable names for onboard Intel E8xx ports

If firmware assigns every onboard E8xx port the same type instance, add `ice.rh_phys_port_name=1 i40e.rh_phys_port_name=1` to the kernel command line. The drivers expose `phys_port_name`, allowing `udev` to create distinct names with an `np<number>` suffix. This is off by default to preserve existing names. (9.8)

### `e1000e` K1 power-state default

K1 is disabled by default on Intel Meteor Lake and newer systems to avoid packet loss, but remains enabled on older platforms. Inspect with `ethtool --show-priv-flags <device>`. Disable explicitly with `ethtool --set-priv-flags <device> disable-k1 on`. (9.8)

## DHCP, DNS, and time

### Early-boot DHCP client identity

Use `rd.net.dhcp.client-id=<id>` to provide a DHCP client ID during early boot when the server identifies initramfs clients by that value. (9.8)

### Chrony 4.8 controls

Chrony 4.8 adds `maxunreach`, `chronyc -u`, `opencommands`, `local waitsynced`, `local waitunsynced`, an RTC refclock, and PHC refclock selection by interface name. Its command socket is hidden to reduce exposure to unsafe permission changes. (9.8)

### Unbound 1.24 administration

Unbound 1.24.2 adds `unbound-control cache_lookup <domains>`, `zone status` for authoritative zones, DNS Error Reporting options, and the `RESINFO` record type. `resolver.arpa` and `service.arpa` join the default locally served zone list. (9.8)

### Name-service cache replacement

`nscd` is removed. Use `systemd-resolved` for DNS caching and SSSD for other name-service caching.

### SSSD dynamic DNS over TLS

SSSD can send dynamic DNS updates over TLS after installing `nsupdate` from `bind9.18-utils`. Configure `dyndns_dns_over_tls` and, when required, `dyndns_tls_ca_cert`, `dyndns_tls_cert`, and `dyndns_tls_key` in `sssd.conf`.

### NetworkManager DHCP client removal

The external `dhclient` utility is removed, and `dhcp=dhclient` is invalid in `NetworkManager.conf`. Use NetworkManager's default `dhcp=internal` client.

## IPsec and transport controls

### Multi-subnet IPsec and native Libreswan defaults

The NetworkManager Libreswan plugin can place multiple `leftsubnets` and `rightsubnets` in one tunnel. In Nmstate YAML, `nm-auto-defaults: false` prevents NetworkManager from injecting defaults and lets Libreswan apply its own. It defaults to `true` for compatibility. (9.8)

### Minimal Libreswan packaging

`libreswan-minimal` omits `systemd` and optional-tool dependencies from the full package, providing IPsec in smaller non-systemd container images. (10.2)

### On-demand IPsec listeners

Set the NetworkManager Libreswan profile property `nm-connect-mode` to `ondemand`. If the remote endpoint is unreachable, the tunnel keeps listening so an incoming peer can initiate it later. (10.2)

### Lower TCP retransmission ceilings

The `tcp_rto_max_ms` sysctl can lower TCP's maximum retransmission timeout from the 120000 ms default. Per-socket `TCP_RTO_MAX_MS` takes precedence. (10.2)

### AF_VSOCK namespace isolation

The read-only `net.vsock.ns_mode` reports whether a network namespace uses global or private-local CID allocation. Set the mode inherited by future children with `net.vsock.child_ns_mode`; its first write locks the value, and a local namespace cannot create global children. (10.2)

## nftables and firewalld

### Dynamic nftables netdev hooks

Netdev-family chains and flowtables can bind an interface name before the interface exists and can use suffix wildcards. Hooks activate as matching interfaces appear instead of failing the transaction. Inspect active bindings with `nft list hooks`. (10.2)

### Firewalld policy sets

Firewalld policy sets are reusable policy collections. The `gateway` set enables masquerading, connection-tracking helpers, and forwarding between zones as a router baseline. (10.2)

### Firewalld lockdown removal

Firewalld's lockdown feature is removed because root processes could add themselves to its allowlist. Replace it with another privilege-control and service-isolation design.

### Removed legacy networking interfaces

Kernel modules for iptables, ip6tables, ipset, ebtables, and arptables move to `kernel-modules-extra`; ATM is disabled. The obsolete `PF_KEYv2` IPsec API is removed, so applications must use netlink.

## Major-version profile migration

### Network configuration migration

Network teams, `teamd`, and `libteam` are removed. Convert team profiles to kernel bonds before upgrading. NetworkManager no longer supports ifcfg files under `/etc/sysconfig/network-scripts`; migrate connections to keyfiles under `/etc/NetworkManager/system-connections`.

### iPXE firmware-driver dependency

The `ipxe-roms` subpackage and generic driver-bearing iPXE EFI, disk, ISO, kernel, and USB images are removed. Use `ipxe-snponly-x86_64.efi` or `undionly.kpxe`; these depend on platform firmware for the NIC driver.

### NetworkManager profile-file access mitigation

Private profiles cannot reference another user's certificate, but a locally logged-in non-root user can still create a system profile that does. Restrict the PolicyKit action to administrators: (9.8)

```javascript
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.NetworkManager.settings.modify.system" &&
        !subject.isInGroup("wheel"))
        return polkit.Result.AUTH_ADMIN_KEEP;
});
```
