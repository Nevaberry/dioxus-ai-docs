# Security, identity, and cryptography

## Contents

- [Host integrity and policy enforcement](#host-integrity-and-policy-enforcement)
- [OpenSSH and privileged execution](#openssh-and-privileged-execution)
- [Crypto policy and post-quantum migration](#crypto-policy-and-post-quantum-migration)
- [Encrypted storage and device onboarding](#encrypted-storage-and-device-onboarding)
- [Identity Management administration](#identity-management-administration)
- [SSSD, PAM, and authentication](#sssd-pam-and-authentication)
- [Directory Server](#directory-server)
- [Compliance tooling and previews](#compliance-tooling-and-previews)

## Host integrity and policy enforcement

### AIDE 0.19 configuration migration

AIDE 0.19.2 replaces `libmhash` with `libnettle`. Rename `database`, `summarize_changes`, and `grouped` to `database_in`, `report_summarize_changes`, and `report_grouped`. Replace `verbose` and `--verbose` with `log_level` and `report_level`. New capabilities include `fstype`-restricted rules, Linux-capability attributes, `--dry-init`, and `--path-check`. (9.8)

### `fapolicyd` filters and database sizing

`fapolicyd` 1.4.3 adds file-rule filtering, filter testing, checks for ignored mounts, and the `fapolicyd-filter.conf(5)` documentation. Set `db_max_size = auto` for automatic database sizing. Default database and subject-cache sizes are larger. (9.8)

### SELinux relabeling controls

`restorecon -c` prints the number of relabeled files and exits successfully only if it changed at least one file. `setfiles -A` lowers memory use on large file systems by disabling conflict tracking for multiply hard-linked inodes. (10.2)

### SELinux policy modules for EPEL

Policies used only by EPEL packages move to `selinux-policy-targeted-extra` and `selinux-policy-mls-extra` in CodeReady Linux Builder. Enable the appropriate CRB content so EPEL dependencies can install these modules.

### Live-patch CVE reporting

`kpatch` reports which CVEs are fixed by live patches on the running base kernel, allowing compliance tooling to distinguish a live-patched system from a vulnerable on-disk kernel version. (9.8)

### Certificate handling in SOS cleanup

`sos clean --treat-certificates` can remove, obfuscate, or retain the original binary form of TLS certificates in a report, allowing certificate material to be handled separately from other scrubbed data. (9.8)

## OpenSSH and privileged execution

### OpenSSH 9.9 behavior and controls

The 9.8 release moves from OpenSSH 8.7 to 9.9. `ssh-keygen` defaults to Ed25519, except under FIPS where it uses RSA. Review `ChannelTimeout`, `PerSourcePenalties`, `CanonicalMatchUser`, `PAMServiceName`, and `EnableEscapeCommandline` for session and authentication policy. The server is split into `sshd` and `sshd-session`; disabling privilege separation or daemon re-execution is unsupported. (9.8)

### Server-side GSSAPI credential delegation control

Set `GSSAPIDelegatedCredentials no` in `sshd_config` to refuse forwarded credentials. The default is `yes` for compatibility. (10.2)

### SSH host-key ownership

SSH host keys return to mode `0600`, and the `ssh_keys` group is removed. `ssh-keysign` uses SUID instead of SGID. Audit custom permissions and group-based access assumptions.

### Sudo 1.9.17 policy controls

Sudoers supports regular expressions, `log_subcmds`, `intercept`, compact JSON logging, a configurable denial message, and separate stdin, stdout, stderr, and TTY logging controls. `sudo -N` performs a no-update operation. (9.8)

## Crypto policy and post-quantum migration

### Post-quantum TLS and SSH policy

GnuTLS 3.8.10 supports hybrid ML-KEM exchange and ML-DSA-44, -65, and -87 signatures when the `PQ` system-wide subpolicy is active. TLS certificate compression is available but disabled by default. The same subpolicy enables OpenSSH `mlkem768x25519-sha256` exchange when the peer supports it. (9.8)

### Post-quantum-only `FUTURE` policy

The `FUTURE` crypto policy removes traditional key exchange and permits only hybrid ML-KEM methods. It intentionally breaks broad interoperability: affected hosts cannot reach the Red Hat CDN, and Java clients cannot connect to TLS servers under this policy. (10.2)

### Cryptographic API migrations

OpenSSL's ENGINE API is deprecated, `engine.h` is removed, and builds see `OPENSSL_NO_ENGINE`; migrate to providers. Replace deprecated `oqsprovider` and `liboqs` with OpenSSL 3.5 PQC. Every GnuTLS crypto policy except `LEGACY` disables RSA PKCS #1 v1.5 encryption and decryption. (10.2)

### CA trust and FIPS-mode layout

Software that reads `/etc/pki/tls/certs/ca-bundle.crt` directly should use `/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem`. `fips-mode-setup` and `/etc/system-fips` are removed. Install with the `fips=1` kernel argument and verify runtime state in `/proc/sys/crypto/fips_enabled`.

### OpenSSL compatibility and PKCS #11 migration

`compat-openssl11` is removed; build applications against OpenSSL 3. `pkcs11-provider` replaces the `openssl-pkcs11` engine package. Apache removes the engine-based `SSLCryptoDevice` directive, while PKCS #11 URIs remain available through the provider.

### Stricter cryptographic-policy interoperability

`DEFAULT` rejects TLS suites that use RSA key exchange. Select `LEGACY` or a custom subpolicy only for a peer that requires them. `DEFAULT:SHA1` is removed, and even `LEGACY` disallows SHA-1 in TLS unless the application also uses `@SECLEVEL=0`. TLS 1.0 or 1.1 therefore needs both `LEGACY` and that lower security level.

### Post-quantum private-key conversion

OpenSSL 3.5 uses standardized ML-KEM and ML-DSA private-key formats instead of older `oqsprovider` encoding. Convert an old unencrypted key with `openssl pkcs8 -in <old-key> -nocrypt -topk8 -out <standard-key>`.

### Sequoia OpenPGP bundle import limitation

`rust-rpm-sequoia` aborts a multi-certificate import if any included key is forbidden by the active crypto policy, so later certificates are not processed. Remove disallowed keys from the bundle before importing it. (10.2)

### PKCS #11 client packaging

`p11-kit-client.so` moves from `p11-kit-server` into the new `p11-kit-client` subpackage; account for this on minimal hosts and containers. Version 0.26.1 headers implement PKCS #11 3.2 post-quantum definitions, and module configuration can specify an RPC server address. (9.8)

## Encrypted storage and device onboarding

### Trustee-bound LUKS unlocking

`clevis-pin-trustee` releases LUKS keys through remote attestation against a Trustee KBS. The `60clevis-pin-trustee` Dracut module supports root-volume unlock. Bind with `clevis luks bind -d <device> trustee '<config>'`; combine the pin with `tang` or `tpm2` for multi-policy unlock. (9.8)

### LUKS keys across crash kernels

The `/etc/crypttab` option `link-volume-key=` links an activated LUKS2 key into a kernel keyring for another service. On x86_64, `kdumpctl setup-crypttab` uses it so the crash kernel can reopen an encrypted target and save `vmcore` without another passphrase. (9.8)

### Supported Go FDO implementation

The `go-fdo-client`, `go-fdo-server`, `go-fdo-server-manufacturer`, `go-fdo-server-owner`, and `go-fdo-server-rendezvous` packages provide fully supported FIDO Device Onboarding. They are incompatible with the older Technology Preview `fdo-*` RPMs and containers; do not mix the implementations. (10.2)

## Identity Management administration

### IdM character-credit password policies

IdM password policies add `--dcredit`, `--ucredit`, `--lcredit`, and `--ocredit`. Negative values require a minimum count of the character class; positive values credit minimum password length. Do not combine them with `--minclasses`. (9.8)

### IdM system accounts and passkeys

Use `ipasysaccount` for LDAP-authenticated service accounts and `iparole` to grant them password-management privileges. Passwords reset by these external agents do not force a change at next login. `ipapasskeyconfig` controls passkey user verification; user, host, service, and configuration modules accept `passkey` authentication types or indicators. (9.8)

### IdM and Active Directory administration

`ipa-certupdate --force-server <server-fqdn>` refreshes CA trust through a selected reachable IdM server. IdM supports cross-forest trust with Windows Server 2025. `adcli delete-computer --recursive` removes computer objects with children such as BitLocker metadata. CEP/CES enrollment supports GSSAPI channel bindings required by Windows Server 2025 defaults. (9.8)

### `ipa-migrate` omits SSH public keys

`ipa-migrate` does not copy user or ID-override SSH keys. Export them with `ipa user-find --all` or `ldapsearch`, then restore them at the destination with `ipa user-mod --sshpubkey`; otherwise key authentication fails after migration. (9.8)

### Cross-domain IdM automount discovery

`ipa-client-automount --domain <idm-domain>` selects the DNS domain used to discover IdM, avoiding reliance on the client's own DNS domain in cross-domain deployments. (10.2)

### IdM 4.13 lifecycle defaults

New IdM deployments enable random certificate serial numbers and remove certificates 30 days after expiry. NIS server emulation is removed and the Schema Compatibility Tree plugin is deprecated. IdM supports the full 32-bit ID range and permits duplicate CA subject names under constrained trust and nickname conditions. (10.2)

### Post-quantum and HSM-backed IdM certificates

Directory Server accepts TLS certificates using ML-DSA-44, -65, and -87. Certificate System can issue ML-DSA keys and signatures at those levels. On HSM installations, Lightweight CA certificates and private keys are generated on the HSM with token-prefixed names such as `mytoken:lwca`. (10.2)

### `ansible-freeipa` collection naming

The `ansible-freeipa` RPM installs only `freeipa.ansible_freeipa`. Use fully qualified names such as `freeipa.ansible_freeipa.ipahbacrule`. From release 10.1, the RPM collection can also run playbooks written for `redhat.rhel_idm`.

### HSM-backed IdM installation constraint

Install IdM CAs and KRAs with HSM-resident keys by passing `--token-name` and `--token-library-path` to `ipa-server-install`. An existing software-backed CA or KRA cannot be migrated to an HSM; reinstall it with keys on the device.

### IdM DNSSEC and LDAP-discovery controls

IdM DNSSEC is always enabled because `dnssec-enable: no;` is removed, although `dnssec-validation: no;` remains. If an LDAP server prohibits anonymous RootDSE reads, set SSSD `ldap_read_rootdse = authenticated` to defer the read until login or `never` to suppress it.

### FIPS IdM replica blocker

A FIPS-mode release 10 replica cannot join an IdM deployment whose Kerberos master key still uses AES HMAC-SHA1, as can happen in environments created on release 8.6 or earlier. Do not plan the replica until a supported master-key upgrade path exists or the deployment is replaced; no completed SHA-1-to-SHA-2 procedure is provided.

### Windows Server 2012 R2 trust removal

IdM no longer supports configuring Active Directory trusts with Windows Server 2012 R2. (10.2)

## SSSD, PAM, and authentication

### Generic SSSD identity providers preview

The Technology Preview `sssd-idp` provider reads users and groups from Keycloak or Entra ID and authenticates them with the OAuth 2.0 Device Authorization Grant. See `sssd-idp(5)` for configuration. (10.2)

### Removed authentication interfaces

`pam_console` is replaced by `systemd-logind`. AD and IdM enumeration can no longer make `getent passwd` or `getent group` list every directory identity. MIT Kerberos removes RSA PKINIT; `kinit -X flag_RSA_PROTOCOL` has no effect and Diffie-Hellman PKINIT is used.

### Mandatory `authselect` ownership

`authselect-libs` owns `/etc/nsswitch.conf` and selected PAM files, and PAM requires it. Later `authselect` calls overwrite edits outside authselect without prompting or needing `--force`. Put special behavior in a maintained custom profile, or leave management explicitly with `authselect opt-out`.

### Local identities after the SSSD files-provider removal

The SSSD `files` provider and the `with-files-domain` and `with-files-access-provider` profile options are removed. Use the proxy provider when SSSD must handle local identities. New installations use the authselect `local` profile; upgrades convert the former `minimal` profile to `local`.

### Reduced FreeRADIUS support scope

Release 10 does not support the FreeRADIUS MySQL, PostgreSQL, SQLite, unixODBC, Perl, or REST modules. Supported deployments center on IdM through Kerberos, LDAP, or PAM, or Python 3 authentication used as the source of truth for IdM.

## Directory Server

### Online Directory Server certificate refresh

After replacing a Directory Server certificate, run `dsconf <instance> config refresh-certs` to activate it for new TLS connections without restarting `dirsrv`. Existing sessions stay open, though clients can drop LDAPS connections if the CA changed. (10.2)

### Directory Server dynamic groups

Dynamic LDAP groups are off by default. Enable `nsslapd-dynamic-lists-enabled` and configure the object class, membership-URL attribute, and result attribute with `nsslapd-dynamic-lists-oc`, `nsslapd-dynamic-lists-url-attr`, and `nsslapd-dynamic-lists-attr`. (10.2)

### Directory Server replication and MemberOf controls

`dsconf <instance> repl-conflict delete-all "<suffix>"` deletes all replication-conflict entries for a suffix. Narrow MemberOf processing with `memberOfSpecificGroupFilter` and `memberOfSpecificGroupOC`; add exclusions with `memberOfExcludeSpecificGroupFilter`. (10.2)

### CIDR trust ranges for Directory Server HAProxy

The multi-valued `nsslapd-haproxy-trusted-ip` accepts mixed IPv4 and IPv6 CIDR ranges and individual addresses, avoiding one setting per trusted proxy. (10.2)

### Directory Server LMDB migration

New `389-ds-base` instances use LMDB; migrate existing BDB instances. Tune `nsslapd-mdb-max-size`, `nsslapd-mdb-max-readers`, and `nsslapd-mdb-max-dbs` under `cn=mdb,cn=config,cn=ldbm database,cn=plugins,cn=config`. Too small a maximum prevents storing the intended data; an excessive memory-mapped size can reduce performance.

### Directory Server subtree-move control removal

`nsslapd-subtree-rename-switch` is removed, so it can no longer disable cross-subtree moves. Enforce an equivalent restriction with an access-control instruction.

## Compliance tooling and previews

### OpenSCAP 1.4 migration

`libopenscap` is internal and has no supported development subpackage or ABI. `oscap` removes `sds-*`, `rds-*`, `cve`, `cvss`, and `cvrf`, and replaces `--skip-valid` with `--skip-validation`. SCAP Workbench is removed; use `oscap` and `autotailor`. OSPP, CCN Basic, and CCN Intermediate profiles are no longer shipped.

### Current preview features

The IdM Modern Web UI is a Technology Preview at `/ipa/modern-ui` for non-production evaluation. `linux-mcp-server`, which exposes system logs and performance information to MCP clients for troubleshooting, is a Developer Preview. (9.8)
