# Security, Identity, and Cryptography

## Mandatory access control and process protection

New Leap 16 installations cannot select AppArmor, although it can be enabled
afterward. Manual 15.6 migrations preserve it, while
`opensuse-migration-tool` asks whether to retain it or switch to SELinux.
AppArmor 4.1 adds a `priority=<number>` rule prefix; AppArmor 4.0's IP/port-level
network rules still lack upstream kernel support. (leap-16.0-guide)

SLES 16 removes AppArmor and enables SELinux enforcing mode by default, with
policies for more than 400 modules. Selecting an SAP workload changes SELinux
to permissive mode automatically. SLES 16 also supports the Yama security
module for system-wide `ptrace` restrictions.

The later SLES 16.0 revision enables regular-file security protection by
default. Validate workloads that depended on the former unprotected behavior.

## SSH and privilege defaults

New Leap 16 installations make remote root authentication key-only and do not
enable `sshd` if setup supplies only a root password. Upgrades preserve previous
behavior. `openssh-server-config-rootlogin` restores password-based remote root
login when explicitly required.

OpenSSH 9.6p1 on SLES 15 SP6 follows system `crypto-policies` and rejects RSA
keys below 2048 bits. Find affected known-host entries before upgrade and
arrange verified replacements:

```sh
grep ssh-rsa ~/.ssh/known_hosts | ssh-keygen -lf -
```

Use `LEGACY` only for temporary recovery, then immediately restore `DEFAULT`:

```sh
sudo update-crypto-policies --set LEGACY
sudo update-crypto-policies --set DEFAULT
```

The first SLES 16 installer-created user joins `wheel`. Wheel members use their
own password for `sudo -i`, `kexec`, and Polkit; non-members use the root
password. New installations implement this through
`sudo-policy-wheel-auth-self`.

The later SLES 16.0 installer can configure SSH public keys for every created
account, not only a limited account type. (16.0-rev-2026-08-04)

## Identity services

Leap 16 provides `himmelblau` PAM and NSS modules for Azure Entra ID and Intune
authentication.

SLES 16 removes NIS/Yellow Pages; migrate identity service to LDAP. It also
removes WBEM management through SBLIM without a direct replacement. SUSE
Multi-Linux Manager can still manage SLES 16 and use Salt internally, although
SLES 16 itself ships no Salt packages.

SSSD 2.10 can run as `sssd` in non-root containers. Clear its supplementary
group in an override; filesystems without POSIX capabilities, including NFS,
still require root:

```ini
[Service]
User=sssd
Group=sssd
SupplementaryGroups=
```

```sh
systemctl edit sssd.service
systemctl daemon-reload
systemctl restart sssd
```

SLES 16 `libldap` and `liblber` compatibility shims expose OpenLDAP 2.4 sonames
over OpenLDAP 2.6 for applications such as SAP central user management. They
cover only the public API and cannot supply the two GSSAPI functions removed in
2.6.

SLES 15 SP7 reintroduces the OpenLDAP server as `openldap2_5` only to extend the
migration window. Do not use it for new deployments; it is absent from SLES 16,
so continue migration to `389-ds`.

## FIPS and OpenSSL providers

FIPS mode exists in SLES 16.0, but that release is not yet FIPS 140-3 certified.
SHA-1 is disabled or marked unapproved in FIPS mode, and other disabled
algorithms can alter application behavior.

OpenSSL includes MD2 support, but MD2, MD4, and MD5 remain disabled unless the
legacy provider is activated for SQL Server 2025 `HASHBYTE` compatibility.
Enable both providers in `/etc/ssl/openssl.cnf`, then verify with
`openssl list -providers`:

```ini
[provider_sect]
default = default_sect
legacy = legacy_sect

[default_sect]
activate = 1

[legacy_sect]
activate = 1
```

Post-quantum key exchange is enabled by default in the later SLES 16.0 revision.
Test interoperability with PQC negotiation even when no explicit opt-in is
configured.
