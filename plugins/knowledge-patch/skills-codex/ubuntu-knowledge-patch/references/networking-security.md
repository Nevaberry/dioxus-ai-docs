# Networking, Identity, Time, and Security

## Netplan, networkd, and readiness

### DHCP search domains

In Ubuntu 24.10, `systemd-networkd` no longer defaults `UseDomains=true`, so
DHCP-provided search domains are not added to `/etc/resolv.conf`. Set
`UseDomains=true` globally or on the relevant interface when required.

Ubuntu 25.04 cloud images deliberately override that general default with
`UseDomains=true` in
`/etc/systemd/networkd.conf.d/50-cloudimg-settings.conf`, restoring DHCP search
domains for the cloud-image environment.

### Online-state semantics and authentication

Netplan 1.1 in Ubuntu 24.10 waits for link-local addressing and one routable
interface. The installer treats otherwise-unconfigured interfaces as DHCPv4;
remove disconnected entries from `/etc/netplan/50-cloud-init.conf` or mark them
`optional: true`. A Raspberry Pi server using network-dependent cloud-init data
must instead have at least one `optional: false` interface.

Netplan 1.1.2 in Ubuntu 25.04 adds `wpa-psk-sha256` Wi-Fi authentication and
NetworkManager-backed `routing-policy`. Ubuntu also requires configured DNS
servers to be reachable before wait-online considers an interface online.

Netplan 1.1.2ubuntu3 in Ubuntu 25.10 supports non-standard Open vSwitch
arrangements, including OVS running inside snap environments.

## OpenSSL and TLS

OpenSSL 3.3 in Ubuntu 24.10 loads configuration drop-ins from
`/etc/ssl/openssl.conf.d`, a package-safe location for local customization.

OpenSSL 3.5.3 in Ubuntu 25.10 adds server-side QUIC and the ML-KEM, ML-DSA, and
SLH-DSA post-quantum algorithms. Its default TLS supported-groups list includes
and prefers hybrid post-quantum KEM groups; test peers and any strict group
allowlists.

## OpenSSH

### User environment and packaging

Ubuntu 24.10 removes the deprecated `user_readenv=1` use of `pam_env.so` from
OpenSSH PAM configuration. SSH logins no longer import the target user's
`~/.pam_environment`. Move needed variables to a supported mechanism such as
server-side `AcceptEnv` and client-side `SendEnv`.

OpenSSH 9.9 in Ubuntu 25.04 adds `PerSourcePenalties`, default-enabled
`mlkem768x25519-sha256` hybrid post-quantum key exchange, and `Match invalid-user`.
Ubuntu adds `sshd.service` as an alias for `ssh.service` plus GSSAPI client and
server metapackages, and it no longer generates DSA host keys.

### OpenSSH 10 configuration and compatibility

In Ubuntu 25.10, OpenSSH 10 accepts globs in `AuthorizedKeysFile` and
`AuthorizedPrincipalsFile`. Client or server configuration can use
`Match version`, `Match sessiontype`, and `Match command`. DSA support is
removed.

The protocol banner is `SSH-2.0-OpenSSH_10.0`; compatibility logic must not
interpret `OpenSSH_1*` as every 10.x version. Google Cloud's browser SSH button
does not work with Ubuntu 25.10 because it requires the deprecated
`diffie-hellman-group-exchange-sha256` and
`diffie-hellman-group14-sha1` algorithms.

## Identity services

### SSSD failover and LDAP

SSSD in Ubuntu 24.10 adds `failover_primary_timeout`, controlling how often a
primary server is retried after successful failover to a backup. Its default is
the former hard-coded 31 seconds.

SSSD 2.10.1 in Ubuntu 25.04 enables LDAP StartTLS by default. Cache upgrades are
automatic and `sssctl cache-upgrade` is removed. Remove the deleted
`config_file_version` and `reconnection_retries` options from configuration.

### authd providers and administration

Ubuntu 25.04 `authd` supports Google identity in addition to Entra ID. Ubuntu
25.10 adds Entra ID device registration and the `authctl` administration
command.

## AppArmor and user namespaces

Ubuntu 25.04 supplies `bwrap-userns-restrict`, which lets Bubblewrap create a
user namespace before transitioning the workload to tighter confinement but
restricts namespace creation even for privileged invocations. Direct
user-namespace allowances are removed from BusyBox and Nautilus: BusyBox
`unshare` cannot create an unprivileged user namespace, and unusual
Bubblewrap/Nautilus workflows may require local AppArmor rules.

In Ubuntu 25.10, Flatpak application installation can fail because the
`fusermount3` AppArmor profile lacks required rules. An AppArmor profile can also
be attached to the wrong process in Questing LXD containers and unexpectedly
block shell redirection such as `<tool> > output.log`.

## Time synchronization

Ubuntu 24.10 moves Ubuntu NTP pools from `/etc/chrony/chrony.conf` to
`/etc/chrony/sources.d/ubuntu-ntp-pools.sources`. Keeping a locally modified
`chrony.conf` during upgrade does not suppress the new snippet; remove duplicate
pool definitions.

Chrony in Ubuntu 25.04 defaults to Ubuntu Network Time Security servers. NTS key
exchange uses TCP 4460 and time service uses UDP 123. The bootstrap CA and
configuration are `/etc/chrony/nts-bootstrap-ubuntu.crt` and
`/etc/chrony/conf.d/ubuntu-nts.conf`. Networks unable to reach those endpoints
must restore ordinary NTP entries in the Ubuntu pool source snippet or time sync
will fail.

Chrony 4.7 replaces `systemd-timesyncd` as the preinstalled default in Ubuntu
25.10. Migrate an existing installation with:

```sh
apt-mark auto systemd-timesyncd
apt install chrony
```

## Network-service compatibility

### HAProxy, FreeRADIUS, and Squid

HAProxy 3.0 in Ubuntu 25.04 rejects accidental multiple Runtime API commands,
the `enabled` keyword for dynamic servers, and more non-standard URI forms.
Rename `tune.ssl.ocsp-update` to `tune.ocsp-update` before upgrading.

FreeRADIUS 3.2.7 removes `radlast` and its dependency on the removed,
non-2038-safe `last`/32-bit `wtmp` mechanism. Use another accounting source.

Squid 6.13 removes the `-l` option from `ext_time_quota_acl`.

### Open vSwitch TLS and flow handling

OVS 3.5 in Ubuntu 25.04 accepts TLS ranges such as `TLSv1.2+` and
`TLSv1.2-TLSv1.3`, can explicitly configure TLS 1.3 ciphersuites, and deprecates
TLS 1.0 and 1.1. It adds `ovs-flowviz` and enables IPv4 and IPv6 prefix tracking
by default.

### IPsec proposal migration

The strongSwan 6.0 transition in Ubuntu 25.10 removes the NTRU post-quantum
encryption algorithm. Replace any proposal that depends on it.
