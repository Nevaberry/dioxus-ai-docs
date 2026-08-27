# Security, Identity, and Cryptography

## Mandatory access control

### Leap AppArmor behavior (`leap-16.0-guide`)

New Leap 16 installations cannot select AppArmor as the LSM, but administrators
can enable it after installation. Manual 15.6 migrations preserve it; the
openSUSE migration tool asks whether to preserve it or switch to SELinux.

AppArmor 4.1 adds the `priority=<number>` rule prefix. The IP/port-granular
network rules introduced in 4.0 still lack upstream kernel support.

### SLES 16 SELinux default

SLES 16 removes AppArmor and enables SELinux enforcing mode by default, with
policies for more than 400 modules. Configuring SAP workloads automatically
changes SELinux to permissive mode; account for that deliberate exception.

## SSH and local privilege

### Remote root defaults (`leap-16.0-guide`)

New Leap installations allow root SSH by key only. If setup provides only a
root password, it does not enable `sshd`; upgrades retain prior behavior.
`openssh-server-config-rootlogin` restores password-based remote root login.

### OpenSSH system crypto policy

On SLES 15 SP6, OpenSSH 9.6p1 follows system `crypto-policies` and rejects RSA
keys smaller than 2048 bits. Find affected `known_hosts` entries and arrange a
verified replacement key before upgrading:

```sh
grep ssh-rsa ~/.ssh/known_hosts | ssh-keygen -lf -
```

If recovery requires the insecure policy, use `LEGACY` only temporarily and
restore `DEFAULT` immediately:

```sh
sudo update-crypto-policies --set LEGACY
sudo update-crypto-policies --set DEFAULT
```

### Sudo authentication split

On new SLES 16 installations, the first installer-created user joins `wheel`.
Wheel members use their own password for `sudo -i`, `kexec`, and Polkit;
non-members supply the root password. The default is implemented by
`sudo-policy-wheel-auth-self`.

### Per-user primary groups (`leap-16.0-guide`)

With `USERGROUPS_ENAB` in `/usr/etc/login.defs`, new users get a same-named
primary group instead of the shared `users` group, including on upgrades without
an `/etc/login.defs` override. Audit `@users` policy and inherited home-directory
ownership. For a simple home that uses no other group:

```sh
chgrp -R myuser "$HOME"
```

### Installer SSH keys (`16.0-rev-2026-08-04`)

Agama can configure public keys for every account it creates.

## Identity services

### Azure Entra ID on Leap 16 (`leap-16.0-guide`)

`himmelblau` integrates Azure Entra ID and Intune through PAM and NSS and is the
distribution-provided Entra-backed identity path.

### Yama ptrace restrictions

SLES 16 supports Yama system-wide scopes that restrict which processes can
observe or manipulate others through `ptrace`.

### NIS removal

SLES 16 removes NIS/Yellow Pages. Migrate identity services to LDAP.

### OpenLDAP migration window

SLES 15 SP6 announced OpenLDAP end of support with that service pack in favor
of 389 Directory Server. SP7 reverses immediate removal by reintroducing the
server as `openldap2_5` to extend the migration window. It is not for new
deployments and is not planned for SLES 16; continue migration to `389-ds`.

### OpenLDAP 2.4 ABI shims

SLES 16 supplies `libldap` and `liblber` shims with OpenLDAP 2.4 sonames linked
to OpenLDAP 2.6 for applications such as SAP central user management. They
support the public API only and cannot supply the two GSSAPI functions removed
from OpenLDAP 2.6.

### Unprivileged SSSD

SSSD 2.10 can run as user `sssd` for non-root containers. Clear the default
supplementary group in an override:

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

Filesystems without POSIX capabilities, including NFS, still require root.

### SAP PAM migration rewrite

The SLES 16 migration tool replaces obsolete SAP Host Agent references in
`/etc/pam.d/` from `pam_unix_auth.so`, `pam_unix_acct.so`,
`pam_unix_session.so`, and `pam_unix_passwd.so` to `pam_unix.so`; the old
compatibility links no longer exist.

## Cryptographic policy

### OpenSSL development package conflict

SLES 15 SP6 OpenSSL 3.1.4 replaces 1.1.1. The development packages are mutually
exclusive and conflict resolution is not automatic; remove
`libopenssl1_1-devel` manually during upgrade.

### FIPS status on SLES 16

FIPS mode is available, but SLES 16.0 is not yet FIPS 140-3 certified. SHA-1 is
disabled or unapproved in that mode, and other disabled algorithms can alter
application behavior.

### Legacy hashes for SQL Server 2025

OpenSSL is built with MD2, but MD2, MD4, and MD5 remain disabled until the
legacy provider is enabled for SQL Server `HASHBYTE` compatibility. Activate
both providers in `/etc/ssl/openssl.cnf` and verify with
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

### Post-quantum key exchange (`16.0-rev-2026-08-04`)

Post-quantum key exchange is enabled by default. Interoperability tests must
account for PQC negotiation without an explicit opt-in.

### Regular-file hardening (`16.0-rev-2026-08-04`)

Regular-file security protection is enabled by default. Recheck workloads that
depended on the previous unprotected behavior.
