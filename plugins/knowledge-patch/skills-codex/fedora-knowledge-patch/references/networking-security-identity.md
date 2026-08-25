# Networking, Security Policy, and Identity

## Contents

- Network profiles and host networking
- Firewall backends
- Cryptography, trust, and Secure Boot
- Identity, PAM, polkit, and login records

## Network profiles and host networking

### NetworkManager keyfiles replace ifcfg (41)

NetworkManager no longer supports ifcfg profiles. The
`NetworkManager-initscripts-ifcfg-rh`,
`NetworkManager-dispatcher-routing-rules`, and
`NetworkManager-initscripts-updown` packages are gone. Automatic conversion to
native keyfiles has been enabled since Fedora 39; systems that disabled it must
convert remaining files below `/etc/sysconfig/network-scripts` before an
upgrade.

### Legacy network-scripts are removed (41)

The `network-scripts` package, `network.service`, `ifup`, and `ifdown` are
removed, including their support for local custom network scripts. Use
NetworkManager or systemd-networkd, for example:

```console
nmcli connection up CONNECTION
nmcli connection down CONNECTION
```

### Predictable network names in Fedora Cloud (41)

Fedora Cloud images do not add `net.ifnames=0`. New instances use predictable
interface names rather than `eth0`, `eth1`, and so on; provisioning must
discover or use the actual names.

### Workstation's IPv6 reverse-path filter is loose (42)

Workstation sets firewalld's `IPv6_rpfilter` default to `loose`, rather than
upstream's `strict`, so connectivity checks work on multihomed hosts. Upgrades
adopt the value only when `/etc/firewalld/firewalld.conf` was not customized.

## Firewall backends

### Libvirt virtual networks prefer nftables (41)

Libvirt's virtual-network backend creates an isolated `libvirt_network`
nftables table; `nwfilter` still uses iptables and ebtables. Docker's iptables
`FORWARD` policy and non-firewalld firewall managers can block guest traffic.
If needed, restore the compatibility backend and restart `virtnetworkd`:

```ini
# /etc/libvirt/network.conf
firewall_backend = "iptables"
```

```console
systemctl restart virtnetworkd
```

### Netavark uses nftables (41)

Netavark creates Podman firewall rules with nftables by default. Inspect and
integrate host firewalls with nftables rather than looking only at iptables.
Podman 6's later removal of the iptables backend is detailed in
[atomic-cloud-containers.md](atomic-cloud-containers.md).

## Cryptography, trust, and Secure Boot

### SHA-1 signatures are rejected by OpenSSL (41)

The default crypto policy blocks both creating and verifying SHA-1 signatures.
As a temporary weaker bridge, set the system-wide policy with
`update-crypto-policies --set FEDORA40`, or run one process as
`runcp FEDORA40 command args` when the extra policy tool is installed.

### NVIDIA Secure Boot enrollment (41)

GNOME Software offers the proprietary NVIDIA driver on Secure Boot systems and
creates a Machine Owner Key to sign it. The user must enroll that key through
the firmware-facing MOK interface on the next reboot.

### Legacy CA bundle paths are removed (44)

The following are removed, along with their `/etc/ssl` symlink paths:

- `/etc/pki/tls/cert.pem`
- `/etc/pki/tls/certs/ca-certificates.crt`
- `/etc/pki/tls/certs/ca-bundle.crt`
- `/etc/pki/tls/certs/ca-bundle.trust.crt`

Use TLS-library defaults or
`/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem`. An end user can
temporarily recreate old bundles until the next `ca-certificates` update or
reinstall with:

```console
update-ca-trust extract --rhbz2387674
```

## Identity, PAM, polkit, and login records

### SSSD runs with reduced privileges (41)

SSSD defaults to the `sssd` service user and drops root capabilities even if
the configured service user is `root`; only a few helpers retain privilege.
Custom integrations must not assume the main daemon has unrestricted root
access.

### SSSD SSH known-hosts command replacement (41)

`sss_ssh_knownhostsproxy` is removed. Replace it with
`sss_ssh_knownhosts` and update the corresponding configuration or command-line
integration.

### `pam_ssh_agent_auth` is removed (42)

The `pam_ssh_agent_auth` package and PAM component are unavailable. Replace
PAM policies that delegated authorization to keys in an SSH agent before
upgrading.

### `lastlog2` replaces the legacy login database (43)

util-linux's Y2038-safe `lastlog2` and `pam_lastlog2` replace `lastlog` and
`pam_lastlog`, using SQLite. Existing `/var/log/lastlog` data is migrated
automatically and a `lastlog` command symlink remains, but PAM configuration
and direct database integrations must use the new implementation.

### Atomic Desktops stop accepting pkla polkit rules (44)

Atomic Desktops no longer support deprecated `.pkla` authorization rules,
matching other OSTree and bootable-container images. Convert policy to current
polkit JavaScript rules.
