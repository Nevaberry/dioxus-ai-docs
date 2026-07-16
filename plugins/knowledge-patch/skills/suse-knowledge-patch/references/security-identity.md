# Security, Identity, and Cryptography

Use this reference for mandatory access control, login policy, PAM, SSH, directory services, FIPS, and cryptographic compatibility.

## Contents

- [Mandatory access control](#mandatory-access-control)
- [Local and remote authentication](#local-and-remote-authentication)
- [SSH and system cryptography](#ssh-and-system-cryptography)
- [Directory and identity services](#directory-and-identity-services)
- [PAM migration](#pam-migration)
- [Security-focused containers](#security-focused-containers)

## Mandatory access control

### Leap AppArmor and SELinux choices

Leap 16 new installations cannot select AppArmor as the Linux Security Module, although it can be enabled after installation. Manual Leap 15.6 migrations preserve AppArmor; `opensuse-migration-tool` prompts to preserve it or switch to SELinux.

AppArmor 4.1 adds a `priority=<number>` rule prefix. AppArmor 4.0's IP- and port-granular network rules still lack upstream kernel support.

### SLES SELinux-only policy

SLES 16 removes AppArmor and enables SELinux in enforcing mode by default, with policies for more than 400 modules. Configuring SLES for SAP workloads automatically changes SELinux to permissive mode.

### Yama

SLES 16 supports Yama system-wide scopes for restricting which processes may observe or manipulate other processes through `ptrace`.

## Local and remote authentication

### Primary user groups

With `USERGROUPS_ENAB` enabled in `/usr/etc/login.defs`, Leap 16 creates a same-named primary group for each new user instead of using the common `users` group. This also affects upgrades that did not override `/etc/login.defs`. Audit policy based on `@users` and inherited home-directory group ownership. Convert a home that uses no other group with:

```sh
chgrp -R myuser "$HOME"
```

### Sudo and Polkit

The first SLES 16 installer-created user joins `wheel`. Wheel members use their own password for `sudo -i`, `kexec`, and Polkit; non-members use the `root` password. New installations implement the default through `sudo-policy-wheel-auth-self`.

### Remote root SSH

Leap 16 new installations allow root SSH authentication by key only and do not enable `sshd` when setup supplies only a root password. Upgrades preserve prior behavior. Install `openssh-server-config-rootlogin` only when password-based remote root login is deliberately required.

### Cockpit root login

Leap 15.6 disables Cockpit password login for `root` through `/etc/cockpit/disallowed-users`. Remove the entry only deliberately and restart `cockpit.socket`.

## SSH and system cryptography

### OpenSSH policy

SLES 15 SP6 OpenSSH 9.6p1 follows system `crypto-policies` and rejects RSA keys smaller than 2048 bits. Find affected `known_hosts` entries and arrange a verified replacement host key:

```sh
grep ssh-rsa ~/.ssh/known_hosts | ssh-keygen -lf -
```

Use the insecure `LEGACY` policy only for temporary recovery, then restore `DEFAULT` immediately:

```sh
sudo update-crypto-policies --set LEGACY
sudo update-crypto-policies --set DEFAULT
```

### FIPS and SHA-1

SLES 16.0 provides FIPS mode but is not yet FIPS 140-3 certified. SHA-1 is disabled or marked unapproved in that mode, and other disabled algorithms can also affect applications.

### Legacy OpenSSL hashes

SLES 16 OpenSSL is built with MD2, but MD2, MD4, and MD5 stay disabled until the legacy provider is active. For SQL Server 2025 `HASHBYTE` compatibility, enable both providers in `/etc/ssl/openssl.cnf`:

```ini
[provider_sect]
default = default_sect
legacy = legacy_sect

[default_sect]
activate = 1

[legacy_sect]
activate = 1
```

Verify with `openssl list -providers`. Do not enable the legacy provider without a compatibility requirement.

## Directory and identity services

### Azure Entra ID

Leap 16 supplies `himmelblau` PAM and NSS modules for Azure Entra ID and Intune-backed Linux authentication.

### Unprivileged SSSD

SLES 16 SSSD 2.10 can run as user `sssd` for non-root containers. Clear the default supplementary group in a unit override:

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

Filesystems without POSIX capabilities, including NFS, still require SSSD to run as root.

### OpenLDAP transition

SLES 15 SP6 originally ended OpenLDAP support with the SP6 lifecycle in favor of 389 Directory Server. SLES 15 SP7 reverses immediate removal by reintroducing the server as `openldap2_5` to extend the migration window. Do not use it for new deployments; it is not planned for SLES 16, so continue migration to `389-ds`.

SLES 16 supplies OpenLDAP 2.4-soname compatibility shims for public APIs only; see [packages-runtimes.md](packages-runtimes.md).

### Removed identity protocols

SLES 16 removes NIS/Yellow Pages; migrate its identity roles to LDAP.

## PAM migration

During SLES 16 migration, replace obsolete SAP Host Agent PAM references `pam_unix_auth.so`, `pam_unix_acct.so`, `pam_unix_session.so`, and `pam_unix_passwd.so` with `pam_unix.so`. The migration tool rewrites them because the compatibility links are absent.

## Security-focused containers

A STIG-compliant SLE Base Container Image is available through the US Department of Defense Iron Bank repository. Use that artifact for deployments requiring Iron Bank content instead of assuming the ordinary BCI has equivalent hardening.
