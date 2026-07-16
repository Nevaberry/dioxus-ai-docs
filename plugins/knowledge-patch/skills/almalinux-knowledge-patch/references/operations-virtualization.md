# Operations, Networking, Containers, and Virtualization

Use this reference for fleet administration, networking and logging baselines,
container engines, hypervisors, and AlmaLinux-specific operational behavior.

## Logging, networking, and administration

### Rsyslog hardening

AlmaLinux 9.4 rsyslog adds customizable TLS/SSL encryption settings and more
controls for dropping capabilities (`9.4`).

### Component baselines

| Coverage batch | Administration and network components |
| --- | --- |
| `9.6` | rsyslog 8.2412.0, NetworkManager 1.52.0, and iproute 6.11.0. |
| `9.7` | rsyslog 8.2506.0, PCP 6.3.7, NetworkManager 1.54.0, iproute 6.14.0, and ethtool 6.15. |
| `9.8` | rsyslog 8.2510.0, NetworkManager 1.54.3, and iproute 6.17.0. |
| `10.2` | NetworkManager 1.56.0, nftables 1.1.5, BIND 9.18.33-15, and chrony 4.8. |

## Containers and virtualization

| Coverage batch | Stack baseline |
| --- | --- |
| `9.6` | Podman 5.4.0, Buildah 1.39.4, libvirt 10.10.0, and QEMU-KVM 9.1.0; new `snpguest` and `snphost` packages. |
| `9.7` | Podman 5.6.0 and Buildah 1.41.4. |
| `9.8` | Podman 5.8.0, Buildah 1.43.0, Skopeo 1.22.0, libvirt 11.10.0, and QEMU-KVM 10.1.0. |
| `10.1` | libvirt 11.5.0 and QEMU-KVM 10.0.0. |

### IBM POWER KVM

AlmaLinux 9.6 introduces KVM on IBM Power as a technology preview; the
compatible upstream distribution had not supplied that support since 9.0
(`9.6`). AlmaLinux 10.2 fully enables IBM POWER KVM in its virtualization
stack, graduating that preview (`9.8-10.2-ga`).

### SPICE

AlmaLinux 10 enables SPICE support in both server and client applications,
unlike the compatible upstream distribution (`10.0`).

## AlmaLinux-specific kernel behavior

The AlmaLinux 9.8 kernel backports a dentry-lock race fix for excessive
`systemd` and `ps` CPU use during task cleanup (`9.8`). The fix was not in
the compatible RHEL 9.8 kernel.
