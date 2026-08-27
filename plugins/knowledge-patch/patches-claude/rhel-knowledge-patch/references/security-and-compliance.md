# Security and Compliance

Consult this reference for cryptographic policy, SSH, FIPS, hardware keys, attestation, disk unlocking, SELinux, Audit, and application allowlisting.

## Contents

- [SSH authentication and transport](#ssh-authentication-and-transport)
- [Cryptographic policies, formats, and algorithms](#cryptographic-policies-formats-and-algorithms)
- [FIPS, providers, hardware tokens, and key consumers](#fips-providers-hardware-tokens-and-key-consumers)
- [Attestation and encrypted-volume unlocking](#attestation-and-encrypted-volume-unlocking)
- [SELinux, Audit, fapolicyd, and authorization](#selinux-audit-fapolicyd-and-authorization)

## SSH authentication and transport

### OpenSSH 9.9 compatibility and hardening (10.0)

`ssh-keygen` now defaults to Ed25519 outside FIPS mode and RSA in FIPS mode, DSA support and `pam-ssh-agent` are gone, and host keys return to mode `0600`. New controls include `ChannelTimeout`, `ObscureKeystrokeTiming`, `EnableEscapeCommandline`, `PerSourcePenalties`, and `PAMServiceName`; `ssh-keysign` moves to a separate subpackage.

### TLS session-key logging (10.1)

OpenSSL honors `SSLKEYLOGFILE` and writes secrets in the standard key-log format for traffic decryption during testing. Anyone who can read that file can decrypt the corresponding sessions, so it must not be enabled in production.

### Kerberos authentication indicators in OpenSSH (10.1)

`GSSAPIIndicators` can be used inside `Match` configuration to require or deny Kerberos ticket indicators; once any indicator rule is configured, tickets with no indicators are rejected. The `sshd` system role can manage this option as well.

### Delegated GSSAPI and canonical SSH users (10.2)

`sshd_config` gains `GSSAPIDelegatedCredentials no` to reject forwarded credentials instead of the backward-compatible `yes` default, and `CanonicalMatchUser` makes `Match User` evaluate the password-database username rather than an alias. The `sshd` system role manages the latter with `sshd_CanonicalMatchUser` and separately supports the client-side `GSSAPIDelegateCredentials` setting; in FIPS mode, OpenSSH now permits `gss-group14-sha256`, `gss-group16-sha512`, and `gss-nistp256-sha256` key exchange.

### Hybrid post-quantum SSH (10.2)

OpenSSH adds `mlkem768nistp256-sha256` and `mlkem1024nistp384-sha384`, including under the FIPS policy. Libssh adds those plus `mlkem768x25519-sha256`, which every predefined crypto policy enables at highest priority, along with new `RequiredRsaSize`, client `AddressFamily`, `GSSAPIKeyExchange`, and `GSSAPIKexAlgorithms` controls.


## Cryptographic policies, formats, and algorithms

### Stricter TLS and RSA policy (10.0)

The `DEFAULT` policy rejects TLS RSA key exchange, and `DEFAULT`, `FUTURE`, and `FIPS` make GnuTLS reject RSA PKCS #1 v1.5 encryption; `LEGACY` no longer permits SHA-1 TLS signatures. OpenSSL rejects SHA-1 at `SECLEVEL=2`, and GnuTLS FIPS verification requires RSA keys of at least 2048 bits.

### PKCS #12 and S/MIME policy scopes (10.0)

Crypto policies add `@pkcs12`, `@pkcs12-legacy`, `@smime`, and `@smime-legacy` scopes for NSS-backed operations. OpenSSL and NSS support RFC 9579 PBMAC1 PKCS #12 integrity; NSS generates PBMAC1 in FIPS mode but retains the older MAC by default outside FIPS mode.

### Post-quantum and encrypted-DNS previews (10.0)

Install `crypto-policies-pq-preview`, run `update-crypto-policies --set DEFAULT:TEST-PQ`, and reboot to enable preview PQ algorithms in OpenSSL, GnuTLS, NSS, OpenSSH, liboqs, and oqsprovider. System encrypted DNS is also a Technology Preview: it uses `dnsconfd`/Unbound, has no insecure fallback, and can import a custom CA during installation only through Kickstart `%certificate`.

### Post-quantum cryptography is enabled by default (10.1)

The `LEGACY`, `DEFAULT`, and `FUTURE` policies prioritize hybrid ML-KEM and pure ML-DSA, while `FIPS` enables hybrid ML-KEM and ML-DSA too; NSS and GnuTLS also enable their ML-DSA and hybrid groups. Use the new `NO-PQ` subpolicy to disable PQ algorithms; `TEST-PQ` is no longer the general preview switch and now only enables pure ML-KEM in OpenSSL.

### OpenSSL 3.5 compatibility and key migration (10.1)

OpenSSL 3.5 adds native ML-KEM, ML-DSA, SLH-DSA, QUIC, multiple TLS 1.3 key shares, and opaque `EVP_SKEY` objects, but disables SHA-224 and requires an explicit `xoflen` when finalizing SHAKE-128 or SHAKE-256. Private ML-KEM and ML-DSA keys made by the 10.0 `oqsprovider` must be converted to the standard format with `openssl pkcs8 -in OLD -nocrypt -topk8 -out NEW`.

### Legacy cryptographic compatibility (10.1)

`AD-SUPPORT-LEGACY` is available again for RC4 interoperability with old Active Directory deployments. `oqsprovider` and `liboqs` are deprecated in favor of OpenSSL 3.5, `X25519-MLKEM768` is a deprecated alias for `MLKEM768-X25519`, and HMAC-SHA-1 is deprecated only in FIPS mode.

### GnuTLS 3.8.10 configuration (10.1)

GnuTLS priority files can set `cert-compression-alg`, and TLS supports ML-DSA-44, -65, and -87. A Technology Preview `[provider]` section can point to a PKCS #11 module and PIN; when only an expanded ML-DSA private key exists, derive the required public key separately with `openssl dsa -in PRIVATE -pubout -out PUBLIC`.

### OpenPGP v6 and RPM policy boundaries (10.1)

RPMv6 packages can carry multiple signatures, and Sequoia can handle PQ keys and create or verify OpenPGP v6 signatures; `sq` still cannot generate keys in FIPS mode. The PQ-extended `/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release` cannot be processed by Ansible's GnuPG-backed `rpm_key` modules, and PQ verification is hard-coded on for `rpm-sequoia` even under `NO-PQ`.

### Removed cryptographic compatibility (10.2)

The `FUTURE` crypto policy now permits only hybrid ML-KEM key exchange and removes traditional non-PQ KEX. This intentionally breaks broad interoperability, including CDN access and Java TLS clients in the documented 10.2 configuration.


## FIPS, providers, hardware tokens, and key consumers

### OpenSSL provider transition for hardware keys (10.0)

RHEL replaces the removed `openssl-pkcs11` engine with `pkcs11-provider`; installing the provider automatically enables p11-kit-discovered tokens and lets provider-aware applications use PKCS #11 URIs. The new `tpm2-openssl` package exposes TPM 2.0 keys through the OpenSSL provider API.

### FIPS and hardware-token caveats (10.0)

In FIPS mode, `pkcs11-provider` needs `pkcs11-module-assume-fips = true`; Nginx and wpa_supplicant cannot yet use provider-backed PKCS #11/TPM credentials. TLS 1.2 EMS is mandatory on FIPS systems, breaking legacy peers such as RHEL 7 and pre-vSphere-8 hypervisors that support neither EMS nor TLS 1.3.

### Alternate FIPS provider and hardware keys (10.1)

`fips-provider-next` contains the next provider submitted for validation and is not the default; switch explicitly with `dnf swap openssl-fips-provider fips-provider-next`. `wpa_supplicant` can now load PKCS #11 certificates through `pkcs11-provider`, restoring EAP-TLS authentication with hardware-backed keys.

### PQ certificate fallback for CIM services (10.1)

Pegasus adds `/etc/pki/Pegasus/server-fallback.pem` and `file-fallback.pem`; `sblim-sfcb` adds `sslKeyFallbackFilePath` and `sslCertificateFallbackFilePath`; and OpenWSMAN adds `ssl_key_fallback_file` and `ssl_cert_fallback_file`. These disabled-by-default settings let an ML-DSA certificate coexist with a classic fallback chain.

### OpenCryptoki 3.25 interfaces (10.1)

OpenCryptoki adds PKCS #11 v3 SHA-3/SHAKE, AES and RSA-AES key wrapping, AES-GCM wrapping, EP11 opaque-blob import through `C_CreateObject`, and a P11KMIP key import/export tool. Support varies by the EP11, ICA/Soft, and CCA token back ends.

### Hardware-token tooling (10.2)

OpenCryptoki 3.26 adds `p11sak` wrap/unwrap and password-protected PEM export, HSM-protected TLS client keys in `p11kmip`, larger RSA keys, and IBM ML-DSA/ML-KEM mechanisms across supported token back ends. P11-kit moves `p11-kit-client.so` into the installable `p11-kit-client` subpackage, updates headers to PKCS #11 3.2, and can configure an RPC server address.

### OpenJDK crypto-policy integration (10.2)

The RHEL build of OpenJDK 25 now loads system crypto-policy properties and supports FIPS through NSS.


## Attestation and encrypted-volume unlocking

### Keylime identity, transport, and policy changes (10.0)

The Rust agent adds IDevID/IAK identities (`enable_iak_idevid`, certificate paths, and algorithm selectors), configurable IMA/measured-boot log paths, and TLS 1.3. Revocation webhooks must use HTTPS with a trusted server CA, and `keylime-policy` replaces the former runtime- and measured-boot-policy scripts.

### PKCS #11 unlocking and input-stage logging (10.0)

Clevis 21 adds the `clevis-pin-pkcs11` subpackage for unlocking LUKS volumes with smart cards. Rsyslog 8.2412 can bind a ruleset directly to `imjournal`, allowing filtering and processing before messages enter the main queue.

### Trustee-backed Clevis unlocking (10.2)

The new `clevis-pin-trustee` pin releases LUKS keys only after attestation against a Trustee KBS and includes a `60clevis-pin-trustee` dracut module for root-volume unlock. Bind it with `clevis luks bind -d DEVICE trustee 'CONFIG'`, either alone or in a multi-pin policy with Tang or TPM2.

### Clevis TPM2 configuration validation (10.2)

`clevis-pin-tpm2` now rejects unknown JSON fields instead of silently ignoring misspellings that could create an unbootable LUKS binding.

### Keylime push attestation and TPM keys (10.2)

Keylime adds an agent-driven mode in which agents push attestation data to a verifier, avoiding inbound connectivity for NAT or firewalled nodes. The agent supports TPM-backed ECC P-192 through P-521, RSA 1024/2048/3072/4096, and ECC-signed TLS certificates; payload encryption still uses a separate RSA key.


## SELinux, Audit, fapolicyd, and authorization

### Audit and SELinux administration (10.0)

The new `audisp-filter` plugin allowlists or blocklists Audit events with `ausearch` expressions before forwarding them to downstream plugins. SELinux inverts the file-context equivalence to `/var/run = /run` (custom policy paths must move to `/run`), moves EPEL-only modules to `selinux-policy-epel`, and adds CIL output through `audit2allow -C`.

### Removed security interfaces (10.0)

`scap-workbench` gives way to `oscap`/`oscap-ssh`, installer compliance moves from `oscap-anaconda-addon` to pre-hardened Image Builder output, and CVE OVALv2 data gives way to CSAF/VEX. `fips-mode-setup` and `/etc/system-fips` are gone: enable FIPS at install with `fips=1` and inspect `/proc/sys/crypto/fips_enabled`.

### SELinux packaging and enforcement changes (10.1)

EPEL-only policy moves again, from `selinux-policy-epel` into `selinux-policy-targeted-extra` and `selinux-policy-mls-extra` in CRB, allowing automatic installation when EPEL is enabled. `gnome_remote_desktop_t`, `pcmsensor_t`, and `samba_bgqd_t` become enforcing, while `virtqemud`, `virtvboxd`, `virtstoraged`, and `virtsecretd` remain temporarily permissive.

### Audit and Rsyslog administration (10.1)

The Audit packages add an `auditd.cron` example for time-based log rotation. Rsyslog's `imuxsock` exposes `ratelimit.discarded`, and `imfile` adds module- and per-action `deleteStateOnFileMove` to remove orphaned state when monitored files are rotated or moved.

### SELinux relabeling interfaces (10.2)

`restorecon -c` relabels files, reports the changed-file count, and exits zero only when it relabeled at least one file. `setfiles -A` trades hard-link conflict detection for lower memory use on very large file systems.

### Fapolicyd filtering and database sizing (10.2)

Fapolicyd 1.4.3 adds `--filter`, `--test-filter`, `--check-ignore_mounts`, and `db_max_size=auto` for automatic trust-database sizing. Files matching `/usr/share/*/bin/*` are now included in its trust database.

### NetworkManager profile authorization caveat (10.2)

Local console users can still create system-wide NetworkManager profiles whose certificate paths are read as root. Restrict `org.freedesktop.NetworkManager.settings.modify.system` with a polkit rule when non-wheel users must not create such profiles.

